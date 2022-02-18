from flask import render_template, redirect, flash, url_for
from flask import current_app as app
from flask_login import current_user
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.core import IntegerField
from wtforms.validators import Optional, ValidationError, DataRequired, NumberRange, Length

from flask import Blueprint
from app.models.report import Report


bp = Blueprint('index', __name__)


def post_on_off():
    print('TOGGLE ON/OFF')
    # paradigm should probs be something like a report can be a status update, a summary, or an on/off message
    # then get the last report of a certain type in order to get on/off status


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/status')
def status():
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    with app.db.make_session() as session:
        reports = session.query(Report).all()  # TODO: PAGINATE
        return render_template('status.html', reports=reports)
