# Imports
import cv2
import time
import pandas
import imutils
from slack_functions import slackhook
from dropbox_functions import upload
from datetime import datetime
import json
with open('parameters.json') as f:
    parameters = json.load(f)


# Initiate log dictionaries
lastLog = {}
lastPicture = 0
lastSlack = {}
time_list = []

# Assigning our static_back to None 
last_frame = None

# List when any moving object appear 
motion_list = [None, None]

# Time of movement 
timelist = []

# Initializing DataFrame, one column is start  
# time and other column is end time 
df = pandas.DataFrame(columns=["Start", "End"])

# Capturing video 
video = cv2.VideoCapture(0)

# Infinite while loop to treat stack of image as video 
while True:
    # Reading frame(image) from video 
    check, frame = video.read()

    # resize frame for faster processing
    frame = imutils.resize(frame, width=800)
    (h, w) = frame.shape[:2]

    # Initializing motion = 0(no motion) 
    motion = 0

    # Converting color image to gray_scale image 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Converting gray scale image to GaussianBlur  
    # so that change can be find easily 
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # In first iteration we assign the value  
    # of last_frame to our first frame 
    if last_frame is None:
        last_frame = gray
        continue

    # Difference between last frame  
    # and current frame(which is GaussianBlur) 
    diff_frame = cv2.absdiff(last_frame, gray)  ###
    # diff_frame = fgbg.apply(frame)

    # If change in between static background and 
    # current frame is greater than movementThreshold it will show white color(255)
    thresh_frame = cv2.threshold(diff_frame, parameters["movementThreshold"], 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # Finding contour of moving object 
    cnts = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
        motion = 1

        (x, y, w, h) = cv2.boundingRect(contour)
        # making green rectangle arround the moving object 
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

        # Appending status of motion
    motion_list.append(motion)

    motion_list = motion_list[-2:]

    # Appending Start time of motion 
    if motion_list[-1] == 1 and motion_list[-2] == 0:
        timelist.append(datetime.now())

    # Appending End time of motion
    if motion_list[-1] == 0 and motion_list[-2] == 1:
        timelist.append(datetime.now())

    # Log image
    if motion == 1 and (time.time() - lastPicture > 0.2):
        filename = "logs/" + datetime.now().strftime("%Y-%m-%d %H%M%S.%f") + ".jpg"
        cv2.imwrite(filename, frame)
        #try:
        upload(filename,"/"+filename)
        #except:
        #    print("failed "+filename)
        cv2.imwrite("logs/diffs/" + datetime.now().strftime("%Y-%m-%d %H%M%S.%f") + ".jpg", thresh_frame)
        if time.time() - lastPicture > 3000:
            slackhook('gardenCam',"Got some movement...")
        lastPicture = time.time()

    # Displaying image in gray_scale 
    # cv2.imshow("Gray Frame", gray)

    # Displaying the difference in currentframe to 
    # the staticframe(very first_frame) 
    # cv2.imshow("Difference Frame", diff_frame)

    # Displaying the black and white image in which if 
    # intenssity difference greater than 30 it will appear white 
    # cv2.imshow("Threshold Frame", thresh_frame)

    # Displaying color frame with contour of motion of object
    print(parameters['devMode'])###

    if parameters['devMode']:
        cv2.imshow("Color Frame", frame)

    # Set last frame for comparison in next cycle
    last_frame = gray

    key = cv2.waitKey(1)
    # If q entered whole process will stop 
    if key == ord('q'):
        # if something is moving then it appends the end time of movement
        if motion == 1:
            timelist.append(datetime.now())
        break

# TODO: this doesn't work unless stopped with Q

# Appending time of motion in DataFrame 
for i in range(0, len(time_list), 2):
    df = df.append({"Start": time_list[i], "End": time_list[i + 1]}, ignore_index=True)

# Creating a csv file in which time of movements will be saved 
df.to_csv("movements.csv")

video.release()

# Destroying all the windows 
cv2.destroyAllWindows()

