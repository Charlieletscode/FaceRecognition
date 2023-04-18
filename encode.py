import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime

cred = credentials.Certificate("firebaseKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://facerec-bae67-default-rtdb.firebaseio.com",
    'storageBucket':"facerec-bae67.appspot.com"
})

# import all images and add img to database
path = 'images'
modePathList = os.listdir(path)
imgList = []
studentIds = []

for i in modePathList:
    imgList.append(cv2.imread(os.path.join(path, i)))
    studentIds.append(os.path.splitext(i)[0])

    fileName = f'{path}/{i}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
# print(len(imgList))
print(studentIds)

def findEncode(imgList):
    encodeList = []
    for img in imgList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Start .... ")
encodeListKnown = findEncode(imgList)
encodeListWithIds = [encodeListKnown, studentIds]
# print(encodeListKnown)
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListWithIds, file)
file.close()
print("File is saved")
