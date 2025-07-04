#!/usr/bin/env python3

import numpy as np
import cv2
import imutils
import argparse
from multiprocessing import Process, Queue
import datetime
import os
from pathlib import Path


parser = argparse.ArgumentParser(description="Running an image detection pipeline using multi-process app.")
parser.add_argument("--video", required=True, help="Path to input video")
parser.add_argument("--display", default='yes', choices=['yes', 'no'], 
                    help="give you the option to either display the inferred images or same them to a folder. The yes (default) option is display, the no option is to save.")
parser.add_argument("--shutdown", action="store_true", help="Perform graceful shutdown for the system.")


def display(detections_queue):
    # If relevant, create output directory if it doesn't exist
    display = True
    if args.display == 'no':
        output_path = Path("output_images")
        output_path.mkdir(exist_ok=True)
        display = False
        print(f"Saving images to {output_path} instaed of displaying on screen...")

    counter = 1
    
    while True:
        frame_and_cnts = detections_queue.get()
        if not frame_and_cnts:
            break

        frame, cnts = frame_and_cnts
        mask = frame.copy()

        # I choose arbitrary threshold of 500 for the frame area because this is what they used in the provided code link
        for ct in cnts:
            if cv2.contourArea(ct) < 500:
                continue

            x, y, w, h = cv2.boundingRect(ct)


            # Creating the region of interest, which is the bounding box, for the blur
            roi = frame[y:y + h, x:x + w]
            # Chossing 21x21 blurring kernel as this is what was used in the provided code link
            blurred_roi = cv2.GaussianBlur(roi, (21, 21), 0)
            # Blur only inside the detection coordinates
            mask[y:y + h, x:x + w] = blurred_roi

            frame = mask

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        if not display:
            cv2.imwrite(f"{output_path}/img{counter}.jpg", frame)
        else:
            cv2.imshow("Motion Detection", frame)
            cv2.waitKey(0)

        counter += 1

    if display:
        cv2.destroyAllWindows()


def perform_movement_detection(frame, prev_frame):
    diff = cv2.absdiff(frame, prev_frame)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    return cnts

def detector(frames_queue, detections_queue):
    first_image = True
    prev_frame = None
    while True:
        frame = frames_queue.get()

        if frame is None:
            detections_queue.put(None)
            break

        if first_image:
            first_image = False
            prev_frame = frame
            continue

        cnts = perform_movement_detection(frame, prev_frame)
        detections_queue.put((frame, cnts))

        prev_frame = frame


def streamer(video_path, frames_queue):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("No more frames to read...")
            frames_queue.put(None)
            break

        grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frames_queue.put(grayscale_frame)
    
    cap.release()


def run_detection(video_path):

    q1 = Queue(maxsize=20)
    q2 = Queue(maxsize=20)

    process1 = Process(target=streamer, args=(video_path, q1))
    process2 = Process(target=detector, args=(q1, q2))
    process3 = Process(target=display, args=(q2,))

    process1.start()
    process2.start()
    process3.start()

    process1.join()
    process2.join()
    process3.join()


if __name__ == "__main__":
    args = parser.parse_args()
    video_path = args.video
    run_detection(video_path)
    print("Movement detection finished successfully!")

    if args.shutdown:
        # If Windows OS
        if os.name == "nt":
            os.system("shutdown /s /t 1")
        # If Unix\Linux OS
        elif os.name == "posix":
            os.system("sudo shutdown -h now")
        else:
            print('This code only supports graceful shutdown for Windows and Unix OS.')