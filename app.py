from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, session, redirect, request, jsonify
from functools import wraps
import pymongo
import datetime
import atexit
from flask_cors import CORS
import flask_praetorian
import os
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
from datetime import datetime
from datetime import timedelta
from datetime import timezone

app = Flask(__name__)
jwt = JWTManager(app)

app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config['JWT_SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['REFRESH_KEY'] = os.environ['REFRESH_KEY']
app.config['JWT_COOKIE_SAMESITE'] = "None"
app.config['JWT_CSRF_IN_COOKIES'] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
CORS(app, origins=os.environ['FRONTEND_URL'], supports_credentials=True)


# Database
client = pymongo.MongoClient(os.environ["DB_STRING"])     
db = client.ModernplacesDatabase

from src.ElectricBill import ElectricBill
from src.WaterBill import WaterBill
from src.Guest import Guest
from src.Maintenancelog import Maintenance_log
from src.User import User
from src.Scheduler import Duplicate,Checkwaterflow,UpdatePaymentDue, CheckElectricityLeak,AutoUpdate

# Routes

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@app.route("/api/protected")
@jwt_required()
def protected():
    return jsonify(status="success")


@app.route('/api/maintenance_log/submit', methods=['POST'])
@jwt_required()
def maintenance_log_submit():
    return Maintenance_log().submit()


@app.route('/api/guest/add_guest', methods=['POST'])
@jwt_required()
def guest_add_guest():
    return Guest().Add_Guest()

@app.route('/api/guest/retrieve_room', methods=['POST'])
@jwt_required()
def guest_retrieve_room():
    return Guest().RetrieveRoom()


@app.route('/api/guest/remove_guest', methods=['POST'])
@jwt_required()
def guest_Remove_Guest():
    return Guest().Remove_Guest()

@app.route('/api/guest/retrieve_payment_due')
@jwt_required()
def guest_Retrieve_Payment_Due():
    return Guest().RetrievePaymentDue()

@app.route('/api/guest/remove_payment_due',methods=['POST'])
@jwt_required()
def guest_Remove_Payment_Due():
    return Guest().RemovePaymentDue()


@app.route('/api/guest/retrieve_data', methods=['POST'])
@jwt_required()
def guest_Retrieve_Data():
    return Guest().RetrieveData()


@app.route('/api/waterbill/input', methods=['POST'])
@jwt_required()
def waterbill_input():
    return WaterBill().Input()


@app.route('/api/electricbill/input', methods=['POST'])
@jwt_required()
def electricbill_input():
    return ElectricBill().Input()


# @app.route('/api/user/signup', methods=['POST'])
# def signup():
#     return User().signup()


@app.route('/api/user/signout')
def signout():
    return User().signout()


@app.route('/api/user/login', methods=['POST'])
def login():
    return User().login()


# @app.route('/room_status/submit', methods=['POST'])
# def room_status_submit():
#   return room_status().submit()

# @app.route('/water_usage/submit', methods=['POST'])
# def water_usage_submit():
#   return water_usage().submit()

# @app.route('/elec_usage/submit', methods=['POST'])
# def elec_usage_submit():
#   return elec_usage().submit()


sched = BackgroundScheduler()
sched.add_job(Duplicate, 'cron',
              hour=23, minute=50, misfire_grace_time=60)
sched.add_job(Checkwaterflow, 'cron',
              hour=23, minute=45, misfire_grace_time=60)
sched.add_job(CheckElectricityLeak, 'cron',
              hour=23, minute=47, misfire_grace_time=60)
sched.add_job(UpdatePaymentDue, 'cron',
              hour=23, minute=40, misfire_grace_time=60)
sched.add_job(AutoUpdate, 'cron',
              hour=23, minute=39, misfire_grace_time=60)
sched.start()
