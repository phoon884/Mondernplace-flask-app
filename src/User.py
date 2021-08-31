from flask import Flask, jsonify, request, session, redirect, make_response
from passlib.hash import pbkdf2_sha256
from app import db
import uuid
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
from flask_jwt_extended import get_csrf_token



class User:

    def signup(self):
        print(request.form)

        # Create the user object
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.json['name'],
            "email": request.json['email'],
            "password": request.json['password']
        }

        # Encrypt the password

        user['password'] = pbkdf2_sha256.hash(user['password'])

        # Check for existing email address
        if db.users.find_one({"email": user['email']}):
            return jsonify({"error": "Email address already in use",

                            }), 400

        if db.users.insert_one(user):
            token = create_access_token(identity=user)
            return jsonify({"msg": "signup successful"}), 200

        return jsonify({"error": "Signup failed"}), 400

    def signout(self):
        response = jsonify({"msg": "logout successful"})
        unset_jwt_cookies(response)
        return response, 200

    def login(self):
        print(request.json)
        user = db.users.find_one({
            "email": request.json['email']
        })
        print(datetime.datetime.now())
        if user and pbkdf2_sha256.verify(request.json['password'], user['password']):
            del user['name']
            del user['password']
            access_token = create_access_token(identity=user)
            csrf_token = get_csrf_token(access_token)
            response = jsonify(msg= "login successful",csrf_token=csrf_token)
            set_access_cookies(response, access_token)
            return response

        return jsonify({"error": "Invalid login credentials"}), 401


