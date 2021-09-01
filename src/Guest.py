from src.Helper.checksum_id import checksum_id
from app import db
from flask import Flask, jsonify, request
from datetime import date , datetime
from flask_jwt_extended import decode_token

class Guest:
    def Add_Guest(self):
        try:
            id = request.json['id']                                        #!'id': "X-XXXX-XXXXX-XX-X"
            roomid = request.json['roomid']                              #!'roomid': "A|BXXX
            first_name = request.json['first_name']                      #!'first_name': str
            last_name = request.json['last_name']                        #!'last_name': str
            DoB = request.json['DoB']                                   #!'date': YYYY-mm-dd
            check_in_date = str(date.today().strftime('%Y-%m-%d'))      #!'date': YYYY-mm-dd
            check_out_date = request.json['check_out_date']             #!'date': YYYY-mm-dd
            status = request.json['status']                             #!'status' : Monthly|Daily|Annually|Empty
            rent = request.json['rent']                                  #!'rent' : int
            deposit = request.json['deposit']                            #!'deposit' : int(baht)

            # * VALIDATION
            if not checksum_id(id):
                return {'Status': "Error", "error": "Incorrect ID"}, 400
            room = db.room.find_one({"_id": roomid})
            if not room:
                return {'Status': "Error", "error": "Room does not exist"}, 400
            if room["status"] != "Empty":
                return {'Status': "Error", "error": "Room is currently occupied"}, 400
            guest = db.guest.find_one({"_id": id})

            if guest:
                if guest["currentroom"] != "":
                    return {'Status': "Error", "error": "Guest is already in another room"}, 400
            # * UPDATE GUEST INFO
                rooms = guest["rooms"]
                rooms.append({
                    "roomid": roomid,
                    "check_in_date": check_in_date,
                    "check_out_date": check_out_date
                })

                if not db.guest.update({"_id": id}, {"$set":
                                                     {
                                                         "currentroom": roomid,
                                                         "rooms": rooms
                                                     }}):
                    return {'Status': "Error", "error": "Fail to add guest"}, 500

            else:
                data = {
                    "_id": id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "DoB": DoB,
                    "currentroom": roomid,
                    "rooms": [{
                        "roomid": roomid,
                        "check_in_date": check_in_date,
                        "check_out_date": check_out_date
                    }]
                }
                db.guest.insert_one(data)

                # * UPDATE room INFO
                if db.room.update({"_id": roomid},
                                  {"$set": {"status": status, "guest": id, "rent": rent, "deposit": deposit}}):
                    return {'Status': "Success"}
                else:
                    return {'Status': "Error", "error": "Fatal error report to admin immediately roomid:{0} guestid:{1}".format(roomid, id)}, 500
        except Exception as e:
            print(e)
            return {'Status': "Error", "error": "Internal Error"}, 500

    def Remove_Guest(self):
        try:
            roomid = request.json['roomid']                             #!'roomid': "A|BXXX
            check_out_date = str(date.today().strftime('%Y-%m-%d'))     #!'date': YYYY-mm-dd

            room = db.room.find_one({"_id": roomid})
            if not room:
                return {'Status': "Error", "error": "Room does not exist"}, 400
            if room["status"] == "Empty":
                return {'Status': "Error", "error": "Room is already empty"}, 400
            guest_id = room["guest"]
            if not db.room.update({"_id": roomid}, {"$set": {"status": "Empty", "guest": "", "rent": 0, "deposit": 0}}):
                return {'Status': "Error", "error": "Fail to update room"}, 500

            guest = db.guest.find_one({"_id": guest_id})
            rooms = guest["rooms"]
            rooms[-1]["check_out_date"] = check_out_date
            if db.guest.update({"_id": guest_id}, {
                    "$set": {"currentroom": "", "rooms": rooms}}):
                return {'Status': "Success"}
            else:
                return {'Status': "Error", "error": "Fatal error report to admin immediately roomid:{0} guestid:{1}".format(roomid, id)}, 500

        except Exception as e:
            print(e)
            return {'Status': "Error", "error": "Internal Error"}, 500

    def RetrieveData(self):
        try:
            building = request.json['building']
            floor = int(request.json["floor"])
            print(floor)
            rooms = list(db.room.find({"room.building": building, "room.floor": floor}, {"room": 0,
                                                                                         "deposit": 0,
                                                                                         "guest": 0,
                                                                                         "rent": 0
                                                                                         }))
            print(rooms)

            return {"Status": "Success", "building": building, "data": rooms}, 200
        except Exception as e:
            print(e)
            return {'Status': "Error", "error": "Internal Error"}, 500

    def RetrieveRoom(self):
        try:
            room = request.json['room']              #!'roomid': "A|BXXX
            
            data = db.room.find_one({"_id": room})
            print(data)
            if not data:
                return {'Status': "Error", "error": "Room not found"}, 400
            if data["status"] != "Empty" and data["guest"] != "":
                guest = db.guest.find_one({"_id": data["guest"]})
                data["guest"] = guest
            return {"Status": "Success", "data": data}, 200
        except Exception as e:
            print(e)
            return {'Status': "Error", "error": "Internal Error"}, 500

    def RetrievePaymentDue(self):
        try:
            data = list(db.payment.find({},{"_id":0}).sort("date",-1))
            if not data:
                return {'Status': "Success", "data": []}
            print(data)
            return {'Status': "Success", "data": data}
        except Exception as e:
            print(e)
            return {'Status': "Error", "error": "Internal Error"}, 500
    def RemovePaymentDue(self):
        try:
            data = request.json
            result =  db.payment.delete_one(request.json)
            if result.deleted_count == 0:
                return {"Status": "Error","error":"intended delete data not found"} , 400
            data["date_cleared"] = str(date.today().strftime('%Y-%m-%d'))
            data["authorizer_token"] = decode_token(request.cookies.get('access_token_cookie'))["sub"]["email"]
            data["payment_type"] = "Cash"
            db.payment_log.insert_one(data)
            return {'Status': "Success"},200
        except Exception as e:
            print(e)
            return {'Status': "Error", "error": "Internal Error"}, 500