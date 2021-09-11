from app import db
from datetime import date


def Duplicate():
    date_now = str(date.today().strftime('%Y-%m-%d'))
    date_split = date_now.split('-')
    data = list(db.room.find())
    new = {
        "date": date_now,
        "data_unit": {
            "day": int(date_split[2]),
            "month": int(date_split[1]),
            "year": int(date_split[0])
        },
        "data": data
    }
    db.log_history.insert_one(new)


def Checkwaterflow():
    to_check = list(db.room.find({"status": "Empty"}))
    for room in to_check:
        waterbill = db.waterbill.find_one({"roomid": room["_id"]})
        if waterbill == None:
            db.outlier.insert_one({
                "date": str(date.today().strftime('%Y-%m-%d')),
                "roomid": room["_id"],
                "result": "No water data"
            })
            continue
        if waterbill["unit_change"] != 0 and waterbill["unit_change"] != None:
            if db.guest.find_one({"rooms.roomid": room["_id"], "rooms.check_out_date": str(date.today().strftime('%Y-%m-%d'))}):
                break
            else:
                data = {
                    "source": "water",
                    "roomid": room["_id"],
                    "unit_change": waterbill["unit_change"],
                    "date": str(date.today().strftime('%Y-%m-%d'))
                }
                db.outlier.insert_one(data)


def CheckElectricityLeak():
    to_check = list(db.room.find({"status": "Empty"}))
    for room in to_check:
        elecbill = db.elecbill.find_one({"roomid": room["_id"]})
        if elecbill == None:
            db.outlier.insert_one({
                "date": str(date.today().strftime('%Y-%m-%d')),
                "roomid": room["_id"],
                "result": "No electric data"
            })
            continue
        if elecbill["unit_change"] != 0 and elecbill["unit_change"] != None:
            if db.guest.find_one({"rooms.roomid": room["_id"], "rooms.check_out_date": str(date.today().strftime('%Y-%m-%d'))}):
                break
            else:
                data = {
                    "source": "elec",
                    "roomid": room["_id"],
                    "unit_change": elecbill["unit_change"],
                    "date": str(date.today().strftime('%Y-%m-%d'))
                }
                db.outlier.insert_one(data)


def UpdatePaymentDue():
    date_now = str(date.today().strftime('%Y-%m-%d')).split('-')
    if int(date_now[2]) == 25:
        rooms = list(db.room.find({"status": "Monthly"}))
        for room in rooms:
            guest = db.guest.find_one({"currentroom": room["_id"]})
            db.payment.insert_one({
                "roomid": room["_id"],
                "amount": room["rent"],
                "first_name": guest["first_name"],
                "last_name": guest["last_name"],
                "id": guest["_id"],
                "date": str(date.today().strftime('%Y-%m-%d'))
            })


def AutoUpdate():
    date_now = str(date.today().strftime('%Y-%m-%d'))
    data = list(db.guest.find({"rooms.check_out_date": date_now,
                   "currentroom": {"$ne": ""}}))
    for room in data:
        db.guest.update({"_id": room["_id"]}, {
                    "$set": {"currentroom": ""}})
    
