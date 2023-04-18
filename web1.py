import streamlit as st
import cv2
import os
import face_recognition
import pickle
import cvzone
import numpy as np

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime


cred = credentials.Certificate("firebaseKey.json")
try:
    app = firebase_admin.get_app()
except ValueError:
    app = firebase_admin.initialize_app(cred, {
    'databaseURL':"https://facerec-bae67-default-rtdb.firebaseio.com",
    'storageBucket':"facerec-bae67.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

imgBg = cv2.imread('resource/background.png')
path = ('resource/Modes')
modePath = os.listdir(path)
modeType = 0
counter = 0
imgModeList = []

for i in modePath:
    imgModeList.append(cv2.imread(os.path.join(path, i)))

file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)

# Set the title for the Streamlit app
st.title("Video Capture with OpenCV")

frame_placeholder = st.empty()

# Add a "Stop" button and store its state in a variable
stop_button_pressed = st.button("Stop")
blobs = bucket.list_blobs(prefix='images')
blob_list = list(blobs)

studentIdList = db.reference(f'Students').get()

while cap.isOpened() and not stop_button_pressed:
    ret, frame = cap.read()
    
    if not ret:
        st.write("The video capture has ended.")
        break

    # You can process the frame here if needed
    # e.g., apply filters, transformations, or object detection

    # Convert the frame from BGR to RGB format
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    imgS = cv2.resize(frame, (0,0), None, 0.25, 0.25)
    # imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBg[162:162+480, 55:55+640] = frame
    imgBg[44:44+633, 808:808+414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDist", faceDis)

            matchindex = np.argmin(faceDis)
            # print("Match Index", matchindex)

            if matches[matchindex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 162+y1,x2-x1, y2-y1
                imgBg =  cvzone.cornerRect(imgBg,bbox, rt = 0)
                id = studentIds[matchindex]
                # print("face detected", studentIds[matchindex])
            # else:
            #     print("no face recognize or not in database")

            if counter == 0:
                cvzone.putTextRect(imgBg, "Loading", (275, 400))
                frame_placeholder.image(imgBg, channels="RGB")
                counter = 1
                modeType = 1
        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(id)
                print(studentInfo)
                # get image from db storage
                for i in range (len(blob_list)):
                    if(id in blob_list[i].name.split('.')[0]):
                        print(blob_list[i].name.split('.')[-1], id)
                        data = blob_list[i].download_as_string()
                        array = np.frombuffer(data, np.uint8)
                        imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                        imgStudent = cv2.cvtColor(imgStudent, cv2.COLOR_BGR2RGB)
                # update data of time
                datetimeObject = datetime.strptime(studentInfo['update_time'],
                                                    "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                # print(secondsElapsed)
                ref = db.reference(f'Students/{id}')
                # studentInfo['total_attendance'] += 1 no need for this i want to change come up time only
                ref.child('update_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                if secondsElapsed > 1:
                    ref = db.reference(f'Students/{id}')
                    # studentInfo['total_attendance'] += 1 no need for this i want to change come up time only
                    ref.child('update_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                imgBg[44:44+633, 808:808+414] = imgModeList[modeType]

            if modeType!=3:

                if 10<counter<=20:
                    modeType = 2
                imgBg[44:44+633, 808:808+414] = imgModeList[modeType]
                if(counter<=10):
                    cv2.putText(imgBg,str(studentInfo['year_knowing_Charlie']),(861,125),
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imgBg,str(studentInfo['major']),(1006,550),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(imgBg,str(id),(1006,493),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    
                    # name is special since peoples name are different
                    (wid,height), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1,1)
                    offset = (414-wid)//2
                    cv2.putText(imgBg,str(studentInfo['name']),(808+offset,445),
                                cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)

                    imgBg[175:175+216,909:909+216] = imgStudent
                # cv2.putText(imgBg,str(studentInfo['id']),(910,625 ),
                #             cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
            counter+=1

            if(counter >= 20):
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBg[44:44+633, 808:808+414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    

    # imgBg = cv2.cvtColor(imgBg, cv2.COLOR_BGR2RGB)
    # Display the frame using Streamlit's st.image
    cv2.waitKey(1)
    frame_placeholder.image(imgBg, channels="RGB")

    # Break the loop if the 'q' key is pressed or the user clicks the "Stop" button
    if cv2.waitKey(1) & 0xFF == ord("q") or stop_button_pressed: 
        break

cap.release()
cv2.destroyAllWindows()