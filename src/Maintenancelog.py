from app import db
from flask import Flask, jsonify, request


class Maintenance_log:
    def submit(self):
        try:
            number = db.maintenance_log.count()+1
            maintenance_log = {
                "_id": number,                       
                "roomid": request.json['roomid'],    #!'roomid':str
                "code": request.json['code'],        #!'code':str
                "date": request.json['date'],        #!'date' YYYY-mm-dd
                "cost": int(request.json['cost']),
                "note": request.json['note']
            }
            if(not db.room.find_one({"_id": maintenance_log['roomid']})):
                return jsonify({"error": "Room {id} does not exist".format(id=maintenance_log["_id"])}), 400
            
            if(not db.code.find_one({"code": maintenance_log['code']})):
                return jsonify({"error": "Code {code} does not exist".format(code=maintenance_log["code"])}), 400
            

            if db.maintenance_log.insert_one(maintenance_log):
                return {'Status': "success"}, 200
            return jsonify({"error": "submittion failed"}), 400

        except Exception as e:
            print(e)
            return jsonify({"error": "submittion failed"}), 500
