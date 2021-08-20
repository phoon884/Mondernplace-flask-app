# from flask import Flask
# from app import app 
# from src.User import User
# from src.Maintenancelog import Maintenance_log

# @app.route('/user/signup', methods=['POST'])
# def signup():
#   return User().signup()

# @app.route('/user/signout')
# def signout():
#   return User().signout()

# @app.route('/user/login', methods=['POST'])
# def login():
#   return User().login()

# @app.route('/maintenance_log/submit', methods=['POST'])
# def maintenance_log_submit():
#   return Maintenance_log().submit()

# @app.route('/room_status/submit', methods=['POST'])
# def room_status_submit():
#   return room_status().submit()

# @app.route('/water_usage/submit', methods=['POST'])
# def water_usage_submit():
#   return water_usage().submit()

# @app.route('/elec_usage/submit', methods=['POST'])
# def elec_usage_submit():
#   return elec_usage().submit()