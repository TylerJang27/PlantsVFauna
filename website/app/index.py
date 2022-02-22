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


bp = Blueprint('index', __name__)


def post_on_off():
    print('TOGGLE ON/OFF')
    # paradigm should probs be something like a report can be a status update, a summary, or an on/off message
    # then get the last report of a certain type in order to get on/off status


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


class ToggleForm(FlaskForm):
    device_id = SelectField(_l('Device ID'), coerce=int)
    turn_on = BooleanField(_l('Turn On'))
    submit = SubmitField(_l('Turn On'))


@bp.route('/status', methods=['GET', 'POST'])
def status():
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    with app.db.make_session() as session:
        reports = session.query(Report).all()  # TODO: PAGINATE, FILTER
        form = ToggleForm()
        form.device_id.choices = [d.device_id for d in session.query(Device).all()]
        if form.validate_on_submit():
            print("PRE-SEND")
            device_id = form.device_id.data
            # is_on = form.turn_on.data
            is_on = True
            send_announcement(device_id, is_on)

        return render_template('status.html', reports=reports, form=form)



