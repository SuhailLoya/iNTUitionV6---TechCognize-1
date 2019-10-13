import time
import speech_recognition as sr;
import time

yy = ''

def callback(recognizer, audio):
    try:
        global yy
        yy = 'y' + recognizer.recognize_google(audio)
    except:
        return
    
#Listens for voice commands in the background
r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)
stop_listening = r.listen_in_background(m, callback, phrase_time_limit=2)

from imutils import face_utils
from utils import *
import os
import numpy as np
import pyautogui as pag
import imutils
import dlib
import cv2
import math
from playsound import playsound

#Decreasing the delay from 0.1 to 0 seconds in order to reduce latency
pag.pause = 0

#Standard algorithm for checking if the destination point is inside the circle described from the centre or not
def isInside(circle_x, circle_y, rad, x, y):
    if ((x - circle_x) * (x - circle_x) +
            (y - circle_y) * (y - circle_y) <= rad * rad):
        return True
    else:
        return False

# Thresholds and consecutive frame length for triggering the mouse action.
MOUTH_AR_THRESH = 0.6
MOUTH_AR_CONSECUTIVE_FRAMES = 10
EYE_AR_THRESH = 0.19
EYE_AR_CONSECUTIVE_FRAMES = 5
WINK_AR_DIFF_THRESH = 0.04
WINK_AR_CLOSE_THRESH = 0.19
WINK_CONSECUTIVE_FRAMES = 3
flag = 0

# Initialize the frame counters for each action as well as
# booleans used to indicate if action is performed or not
MOUTH_COUNTER = 0
EYE_COUNTER = 0
WINK_COUNTER = 0
INPUT_MODE = False
EYE_CLICK = False
LEFT_WINK = False
RIGHT_WINK = False
SCROLL_MODE = False
ANCHOR_POINT = (0, 0)
WHITE_COLOR = (255, 255, 255)
YELLOW_COLOR = (0, 255, 255)
RED_COLOR = (0, 0, 255)
GREEN_COLOR = (0, 255, 0)
BLUE_COLOR = (255, 0, 0)
BLACK_COLOR = (0, 0, 0)

# Initialize Dlib's face detector (HOG-based) and then create the facial landmark predictor
shape_predictor = "model/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor)

# Grab the indexes of the facial landmarks for the left and right eye, nose and mouth respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(nStart, nEnd) = face_utils.FACIAL_LANDMARKS_IDXS["nose"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

# Video capture
vid = cv2.VideoCapture(0)
resolution_w = 1366
resolution_h = 768
cam_w = 640
cam_h = 480
unit_w = resolution_w / cam_w
unit_h = resolution_h / cam_h
flag = 1
while True:
    # Grab the frame from the threaded video file stream, resize it, and convert it to grayscale channels
    _, frame = vid.read()
    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=cam_w, height=cam_h)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    rects = detector(gray, 0)

    # Loop over the face detections
    if len(rects) > 0:
        rect = rects[0]
    else:
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        flag = 0
        continue

    # Determine the facial landmarks for the face region, then convert the facial landmark (x, y)-coordinates to a NumPy
    # array
    shape = predictor(gray, rect)
    shape = face_utils.shape_to_np(shape)

    # Extract the left and right eye coordinates
    mouth = shape[mStart:mEnd]
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]
    nose = shape[nStart:nEnd]
    
    # Because we flipped the frame, left is right, right is left.
    temp = leftEye
    leftEye = rightEye
    rightEye = temp

    # Average the mouth aspect ratio together for both eyes
    mar = mouth_aspect_ratio(mouth)
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0
    diff_ear = np.abs(leftEAR - rightEAR)
    nose_point = (nose[3, 0], nose[3, 1])
    
    # Compute the convex hull for the left and right eye, then visualize each of the eyes
    mouthHull = cv2.convexHull(mouth)
    leftEyeHull = cv2.convexHull(leftEye)
    rightEyeHull = cv2.convexHull(rightEye)
    cv2.drawContours(frame, [mouthHull], -1, YELLOW_COLOR, 1)
    cv2.drawContours(frame, [leftEyeHull], -1, YELLOW_COLOR, 1)
    cv2.drawContours(frame, [rightEyeHull], -1, YELLOW_COLOR, 1)

    for (x, y) in np.concatenate((mouth, leftEye, rightEye), axis=0):
        cv2.circle(frame, (x, y), 2, GREEN_COLOR, -1)

    # Check to see if the eye aspect ratio is below the blink
    # threshold, and if so, increment the blink frame counter
    if (yy != ''):
        print(yy)
    if (yy == 'yleft' or yy == 'ylive' or yy == 'yLyft' or yy == "ylift"):
        pag.click(button='left')
        yy = ''
    elif (yy == 'yright' or yy == 'ylight'):
        pag.click(button='right')
        yy = ''
    yy = ''
    if diff_ear > WINK_AR_DIFF_THRESH:

        if leftEAR < rightEAR:
            if leftEAR < EYE_AR_THRESH:
                WINK_COUNTER += 1
                if WINK_COUNTER > WINK_CONSECUTIVE_FRAMES:
                    pag.click(button='left')
                    WINK_COUNTER = 0
        elif leftEAR > rightEAR:
            if rightEAR < EYE_AR_THRESH:
                WINK_COUNTER += 1
                if WINK_COUNTER > WINK_CONSECUTIVE_FRAMES:
                    pag.click(button='right')
                    WINK_COUNTER = 0
        else:
            WINK_COUNTER = 0
    else:
        if (INPUT_MODE):
            if ear <= EYE_AR_THRESH:
                EYE_COUNTER += 1
                if EYE_COUNTER > EYE_AR_CONSECUTIVE_FRAMES:
                    SCROLL_MODE = not SCROLL_MODE
                    if (SCROLL_MODE):
                        playsound("son.mp3")
                    else:
                        playsound("soff.mp3")
                    EYE_COUNTER = 0
            else:
                EYE_COUNTER = 0
                WINK_COUNTER = 0

    if mar > MOUTH_AR_THRESH:
        MOUTH_COUNTER += 1

        if MOUTH_COUNTER >= MOUTH_AR_CONSECUTIVE_FRAMES:
            # if the alarm is not on, turn it on
            INPUT_MODE = not INPUT_MODE
            if (INPUT_MODE):
                playsound('welcome.mp3')
            else:
                playsound("off.mp3")
            MOUTH_COUNTER = 0
            ANCHOR_POINT = nose_point

    else:
        MOUTH_COUNTER = 0
    if (flag == 0):
        ANCHOR_POINT = nose_point
        flag = 1
    if INPUT_MODE:
        cv2.putText(frame, "READING INPUT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
        x, y = ANCHOR_POINT
        nx, ny = nose_point
        w, h = 25, 25
        multiple = 1
        cv2.circle(frame, ANCHOR_POINT, 25, GREEN_COLOR, 2)
        cv2.line(frame, ANCHOR_POINT, nose_point, BLUE_COLOR, 2)
        dir = direction(nose_point, ANCHOR_POINT, w, h)
        x1, y1 = 0, 0
        if (isInside(x, y, 25, nx, ny) == False):
            x1, y1 = (nx - x) / (2.5), (ny - y) / (2)
        drag = 15
        pag.moveRel(x1, y1)
        if dir == 'up':
            if SCROLL_MODE:
                pag.scroll(3)
        elif dir == 'down':
            if SCROLL_MODE:
                pag.scroll(-3)

    if SCROLL_MODE:
        cv2.putText(frame, 'SCROLL MODE IS ON!', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)

    # Show the frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # If the `Esc` key was pressed, break from the loop
    if key == 27:
        break

# Do a bit of cleanup
cv2.destroyAllWindows()
vid.release()

stop_listening(wait_for_stop=False)