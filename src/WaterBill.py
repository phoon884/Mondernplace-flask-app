from app import db
from datetime import datetime, timedelta ,date
from flask import Flask, jsonify, request


class WaterBill:
    def Input(self):
        try:
            raw_data = request.json['data']                               # !'raw_data': list of {roomid: A|BXXX, unit: int}
            raw_date = str(date.today().strftime('%Y-%m-%d'))             # ! 'rate': YYYY-mm-dd
            processed_data = []
            for room in raw_data:
                if db.waterbill.find_one({"date": raw_date, "roomid": room["roomid"]}):
                    return {"error": "Data already in exist"} ,400
                today_date  = date.today()
                date_assigned = datetime.strptime(raw_date, '%Y-%m-%d')
                yesterday = datetime.strptime(
                    raw_date, '%Y-%m-%d')-timedelta(days=1)
                yesterday = str(yesterday.strftime('%Y-%m-%d'))
                yesterday_unit = db.waterbill.find_one(
                    {"date": yesterday, "roomid": room["roomid"]}, {"unit": 1, "_id": 0})
                if yesterday_unit:
                    unit_change = room["unit"] - yesterday_unit["unit"]
                    if unit_change < 0:
                        if yesterday_unit["unit"] % 10000 == yesterday_unit["unit"]:
                            unit_change = 10000 - \
                                yesterday_unit["unit"] + room["unit"]
                        else:
                            unit_change = 100000 - \
                                yesterday_unit["unit"] + room["unit"]
                else:
                    unit_change = None
                date_list = raw_date.split("-")
                year = date_list[0]
                month = date_list[1]
                day = date_list[2]
                data = {
                    "roomid": room["roomid"],
                    "unit": room["unit"],
                    "unit_change": unit_change,
                    "date": raw_date,
                    "data_unit": {
                        "day": int(day),
                        "month": int(month),
                        "year": int(year)
                    }
                }
                db.waterbill.insert_one(data)
            return {"status": "Success"}, 200
        except Exception as e:
            print(e)
            return jsonify({"error": "submittion failed"}), 500