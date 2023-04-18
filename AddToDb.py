import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("firebaseKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://facerec-bae67-default-rtdb.firebaseio.com"
    # note: not sure above
})

ref = db.reference('Students')

data = {
    "963852":
        {"name":"Elon Musk", "major":"Robotics", "year_knowing_Charlie": 0, "update_time": "2023-12-22 12:22:30"},
    "2062579097":
        {"name":"Charlie Chung", "major":"CE", "year_knowing_Charlie": 22, "update_time": "2023-12-22 12:22:30"},
    "6176718599":
        {"name":"Peng Qiu", "major":"ME&CE", "year_knowing_Charlie": 3, "update_time": "2023-12-22 12:22:30"},
    "6178380020":
        {"name":"Deb Chiao", "major":"BME", "year_knowing_Charlie": 3, "update_time": "2023-12-22 12:22:30"},

}

for key, value, in data.items():
    ref.child(key).set(value)
