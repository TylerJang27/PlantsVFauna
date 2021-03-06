from flask import render_template, redirect, flash, url_for
from flask import current_app as app
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.fields.core import IntegerField
from wtforms.validators import Optional, ValidationError, DataRequired, NumberRange, Length
from flask_babel import _, lazy_gettext as _l

from flask import Blueprint
from app.models.report import Report
from app.models.device import Device

from app.pub import send_announcement, ParalelAnnouncement
from app.utils import create_graph

from datetime import datetime as dt, timedelta as td
from sqlalchemy.exc import OperationalError
from sqlalchemy import nullslast
import glob
import os
import pytz
import asyncio


bp = Blueprint('index', __name__)
PAGE_SIZE = 10


def post_on_off():
    print('TOGGLE ON/OFF')
    # paradigm should probs be something like a report can be a status update, a summary, or an on/off message
    # then get the last report of a certain type in order to get on/off status


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/summary', methods=['GET'])
@bp.route('/summary/<int:page>')
def summary(page=0):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    graph_filename = ""
    reports = []
    devices = []
    graph_loc = ""
    with app.db.make_session() as session:
        try:
            # TODO: FIGURE OUT NEXT BUTTON
            reports = session.query(Report).order_by(nullslast(Report.time.desc())).offset(page*PAGE_SIZE).limit(PAGE_SIZE).all()
            has_next = session.query(Report).order_by(nullslast(Report.time.desc())).count() > (page+1)*PAGE_SIZE
            has_prev = page > 0
            devices = [d.device_id for d in session.query(Device).all()]

            reports_limited = session.query(Report).filter(Report.time > (dt.now() - td(hours=24))).all()
            print(len(reports_limited))
            if len(reports_limited) > 0:
                graph_filename = "last_24.png"
                graph_write_path = os.path.join("app/static/assets/img", graph_filename)
                graph_loc = os.path.join("assets/img", graph_filename)
                create_graph([r.time for r in reports_limited], graph_write_path)

        except OperationalError:
            flash("SQL Error.")
        for r in reports:
            if r.time is not None:
                # r.time = r.time.replace(tzinfo=pytz.timezone("UTC")).astimezone(pytz.timezone("US/Eastern"))
                r.time = r.time.replace(tzinfo=pytz.timezone("UTC")).astimezone(pytz.timezone("US/Pacific")).strftime('%Y-%m-%d %H:%M:%S')
        return render_template('summary.html', reports=reports, devices=devices, graph_loc=graph_loc, has_next=has_next, has_prev=has_prev, page=page)


class ToggleForm(FlaskForm):
    turn_on = BooleanField(_l('Turn On'))
    submit = SubmitField(_l('Submit'))


def get_img_path():
    print("ATTEMPTING TO FIND IMG")
    try:
        print(glob.glob('*'))
        list_of_files = glob.glob('app/static/assets/img/thermal/*.png')
        latest_file = max(list_of_files, key=os.path.getctime)
        for f in list_of_files:
            if f != latest_file and not os.path.basename(f).endswith(".json"):
                if os.path.exists(f):
                    os.remove(f)
                    print("Cleaned up", f)
                else:
                    print("File does not exist", f)
        print("LATEST FILE FOUND WAS", latest_file)
        if latest_file is None or latest_file == []:
            return ""
        latest_file = os.path.join("assets/img/thermal", os.path.basename(latest_file))
        print(latest_file)
        return latest_file
        # <img src="/static/ayrton_senna_movie_wallpaper_by_bashgfx-d4cm6x6.jpg">
    except Exception as e:
        print("error finding image", e)
        return ""

def send_thresholds(device):
    device_id = device.device_id
    count_thresh = device.count_thresh
    min_thresh = device.min_thresh
    max_thresh = device.max_thresh
    color_thresh = device.color_thresh
    parallel = ParalelAnnouncement(device_id, is_on, count_thresh, min_thresh, max_thresh, color_thresh)
    parallel.start()

@bp.route('/detail/<int:device>', methods=['GET', 'POST'])
@bp.route('/detail/<int:device>/<int:page>', methods=['GET', 'POST'])
def detail(device, page=0):
    device_id = device
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    with app.db.make_session() as session:
        try:
            reports = session.query(Report).filter(Report.device_id == device).order_by(nullslast(Report.time.desc())).offset(page*PAGE_SIZE).limit(PAGE_SIZE).all()
            has_next = session.query(Report).filter(Report.device_id == device).order_by(Report.time.desc()).count() > (page+1)*PAGE_SIZE
            has_prev = page > 0
        except OperationalError:
            if page > 0:
                return redirect("/detail/{}/{}".format(device, page-1), code=302)
            return redirect("/summary", code=302)

        form = ToggleForm()
        device = session.query(Device).filter(Device.device_id == device).one_or_none()
        # device.manual_on = True  # TODO: REMOVE THIS LINE
        print("DEVICE ON:", device.remote_on)
        if device is None:
            return redirect("/summary", code=302)
        form.turn_on = not device.remote_on
        if form.validate_on_submit():
            print("PRE-SEND")
            is_on = form.turn_on
            # TODO: MAKE ASYNC NEXT LINE
            # asyncio.create_task(send_announcement(device.device_id, is_on))
            # send_announcement(device.device_id, is_on)
            count_thresh = device.count_thresh
            min_thresh = device.min_thresh
            max_thresh = device.max_thresh
            color_thresh = device.color_thresh
            parallel = ParalelAnnouncement(device.device_id, is_on, count_thresh, min_thresh, max_thresh, color_thresh)
            parallel.start()

            device.remote_on = is_on
            session.add(device)
            session.commit()
            return redirect('/detail/{}/{}'.format(device_id, page))
        # TODO: FIX NUMBERING COLUMN
        img_path = get_img_path()
        for r in reports:
            if r.time is not None:
                # r.time = r.time.replace(tzinfo=pytz.timezone("UTC")).astimezone(pytz.timezone("US/Eastern"))
                r.time = r.time.replace(tzinfo=pytz.timezone("UTC")).astimezone(pytz.timezone("US/Pacific")).strftime('%Y-%m-%d %H:%M:%S')
        return render_template('detail.html', reports=reports, form=form, device=device, has_next=has_next, has_prev=has_prev, page=page, img_path=img_path)

class ThresholdForm(FlaskForm):
    count_thresh = IntegerField(_l('Hot Pixel Count Threshold (number pixels, rec: 10)'))
    max_thresh = IntegerField(_l('Max Temperature Threshold (Celsius, rec: 35)'))
    min_thresh = IntegerField(_l('Min Temperature Threshold (Celsius, rec: 15)'))
    color_thresh = IntegerField(_l('Hot Pixel Temperature Threshold (0-99)'))
    submit = SubmitField(_l('Submit'))

@bp.route('/threshold/<int:device>', methods=['GET', 'POST'])
def threshold(device):
    device_id = device
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    with app.db.make_session() as session:


        form = ThresholdForm()
        device = session.query(Device).filter(Device.device_id == device).one_or_none()
        print("DEVICE ON:", device.remote_on)
        if device is None:
            return redirect("/summary", code=302)

        if form.validate_on_submit():
            print("PRE-SEND")

            count_thresh = form.count_thresh.data
            min_thresh = form.min_thresh.data
            max_thresh = form.max_thresh.data
            color_thresh = int(form.color_thresh.data*255/100)
            parallel = ParalelAnnouncement(device.device_id, device.remote_on, count_thresh, min_thresh, max_thresh, color_thresh)
            parallel.start()

            device.count_thresh = count_thresh
            device.min_thresh = min_thresh
            device.max_thresh = max_thresh
            device.color_thresh = color_thresh

            session.add(device)
            session.commit()
            return redirect('/threshold/{}'.format(device_id))
        # TODO: FIX NUMBERING COLUMN
        
        form.count_thresh.data = device.count_thresh
        form.max_thresh.data = device.max_thresh
        form.min_thresh.data = device.min_thresh
        form.color_thresh.data = int(device.color_thresh*100/255)

        return render_template('threshold.html', form=form, device=device_id)
