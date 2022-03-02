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

from app.pub import send_announcement

from sqlalchemy.exc import OperationalError


bp = Blueprint('index', __name__)


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
    with app.db.make_session() as session:
        try:
            reports = session.query(Report).order_by(Report.time.desc()).offset(page*20).limit(20)
            has_next = session.query(Report).order_by(Report.time.desc()).count() > (page+1)*20
            has_prev = page > 0
        except OperationalError:
            flash("No users in the database.")
        users_list = None
        devices = [d.device_id for d in session.query(Device).all()]
        return render_template('summary.html', reports=reports, devices=devices)


class ToggleForm(FlaskForm):
    turn_on = BooleanField(_l('Turn On'))
    submit = SubmitField(_l('Submit'))


@bp.route('/detail/<int:device>', methods=['GET', 'POST'])
@bp.route('/detail/<int:device>/<int:page>', methods=['GET', 'POST'])
def detail(device, page=0):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    with app.db.make_session() as session:
        try:
            reports = session.query(Report).filter(Report.device_id == device).order_by(Report.time.desc()).offset(page*20).limit(20)
            has_next = session.query(Report).filter(Report.device_id == device).order_by(Report.time.desc()).count() > (page+1)*20
            has_prev = page > 0
        except OperationalError:
            if page > 0:
                return redirect("/detail/{}/{}".format(device, page-1), code=302)
            return redirect("/summary", code=302)

        form = ToggleForm()
        device = session.query(Device).filter(Device.device_id == device).one_or_none()
        if device is None:
            return redirect("/summary", code=302)
        form.turn_on = not device.remote_on
        if form.validate_on_submit():
            print("PRE-SEND")
            is_on = form.turn_on.data
            send_announcement(device, is_on)

        return render_template('detail.html', reports=reports, form=form, device=device, has_next=has_next, has_prev=has_prev)
