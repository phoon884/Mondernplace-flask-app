import pymongo

client = pymongo.MongoClient("mongodb://admin:PYRIciOtEre@localhost:27018")
db = client.ModernplacesDatabase
buildings = ["A", "B"]
rooms = ["01", "02", "03", "04", "05", "06", "07",
         "08", "09", "10", "11", "12", "13", "14", "15"]
for building in buildings:
    for floor in range(1, 6):
        for room in rooms:
            if floor == 1:
                if room == "07" and building == "A":
                    break
                elif room == "07" and building == "B":
                    break
            data = {
                "_id": building+str(floor)+room,
                "room": {
                    "building":building,
                    "floor": floor,
                    "room": int(room)
                },
                "status":"Empty",
                "guest": "",
                "rent": 0,
                "deposit": 0
            }
            while True:
                if db.room.insert_one(data):
                    break
print("Done")