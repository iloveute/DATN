# Thu vien phuc vu xu ly anh
import cv2
import numpy as np

# Thu vien phuc vu nhan dang, theo doi, tinh toan toc do
from object_detection import ObjectDetection
import math
import dlib
import time

# Thu vien ohuc vu check IPv4 cua network connection
import socket
import psutil

# Thu vien phuc vu tao Server
import threading
from flask import Response, Flask
from flask import Flask, render_template, redirect, url_for, request
from waitress import serve

classNames = { 0: 'background',
    1: 'aeroplane', 2: 'xe dap', 3: 'bird', 4: 'boat',
    5: 'bottle', 6: 'bus', 7: 'oto', 8: 'cat', 9: 'chair',
    10: 'cow', 11: 'diningtable', 12: 'dog', 13: 'horse',
    14: 'xe may', 15: 'nguoi', 16: 'pottedplant',
    }
def color_list(class_id):
    colorList = [ (255, 0, 0),
    (0, 51, 102), (51, 102, 153), (51, 102, 204), (0, 51, 153),
    (0, 102, 102), (0, 102, 153), (102, 255, 153), (128, 0, 0),(255, 255, 0),
    (153, 204, 0), (102, 0, 51), (102, 0, 204), (153, 0, 204),
    (255, 102, 102), (0, 102, 255), (204, 153, 0)]
    #Color type
    color_type = colorList[class_id]
    return color_type

# Initialize Object Detection
od = ObjectDetection()
global area
area = [(0,300),(1900,300),(1900,800),(0,800)]


def get_ipv4_addresses():
    ipv4_addresses = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ipv4_addresses.append(addr.address)
    return ipv4_addresses

global host,post
port = "8080"

# Lấy địa chỉ IPv4 của network connection đang sử dụng
network_connections = psutil.net_connections()
for nc in network_connections:
    if nc.status == "ESTABLISHED" and nc.type == socket.SOCK_STREAM and nc.laddr.ip in get_ipv4_addresses():
        host = nc.laddr.ip
        break

host = get_ipv4_addresses()[1]

# Use locks for thread-safe viewing of frames in multiple browsers
global thread_lock 
thread_lock = threading.Lock()




# GStreamer Pipeline to access the Raspberry Pi camera
GSTREAMER_PIPELINE = 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3280, height=2464, format=(string)NV12, framerate=21/1 ! nvvidconv flip-method=0 ! video/x-raw, width=960, height=616, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink wait-on-eos=false max-buffers=1 drop=True'


# Create the Flask object for the application
app = Flask(__name__) 

def captureFrames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera khong kha dung! Chuong trinh se chay voi video co san")
        cap = cv2.VideoCapture("/home/tien/Downloads/DO_AN/static/video/clip1.mp4")
    i_frame = 0
    r, fr = cap.read()
    fr = cv2.resize(fr, (960, 540))
    cv2.imwrite("/home/tien/Downloads/DO_AN/static/image/1.jpg",fr)
    
    global track_id,tracking_objects,center_points_prev_frame, count, od,video_frame,frame,count_xemay, count_oto, count_bus, count_xetai,area
    Threshold = area[3][1]-100
    
    while True:
      
        return_key, frame = cap.read()
        i_frame +=1
        output_image = frame.copy()
        # Point current frame
       
        if i_frame%2 != 0:
           continue  

        center_points_cur_frame = []

        # Detect objects on frame
        heightFactor = frame.shape[0] / 300.0
        widthFactor = frame.shape[1] / 300.0
        frame_resized = cv2.resize(frame, (300, 300))
        
        
        (class_ids, scores, boxes) = od.detect(frame_resized)
       
        for class_id,score, box in zip(class_ids, scores,boxes):
            (x, y, w, h) = box
            x = int( widthFactor * x)
            y = int( heightFactor * y)
            w = int( widthFactor * w)
            h = int( heightFactor * h)
            cx = int( (x + x + w) / 2)
            cy = int( (y + y + h) / 2)
            result = cv2.pointPolygonTest(np.array(area,np.int32),(cx,cy), False)
            if result >= 0:
                center_points_cur_frame.append((cx,cy,x,y, class_id))
                cv2.rectangle(output_image, (x, y), (x + w, y + h), color_list(class_id), 4)
                cv2.putText(output_image, "Name: " + str(classNames[class_id]), (x, y - 15), cv2.FONT_HERSHEY_DUPLEX, 0.5, color_list(class_id))
       
        tracking_objects_copy = tracking_objects.copy()
        center_points_cur_frame_copy = center_points_cur_frame.copy()

        for object_id, pt2 in tracking_objects_copy.items():
            object_exists = False
            if object_id:
                object_exists = True
            
            for pt in center_points_cur_frame_copy:
                distance = math.hypot(pt2[0] - pt[0], pt2[1] - pt[1])

               
        # Detect phim Q
        key = cv2.waitKey(30) & 0xff
        if key == 27:
            break

    cap.release()

def encodeFrame():
	global thread_lock
	while True:
		# Acquire thread_lock to access the global video_frame object
		with thread_lock:
			global video_frame
			if video_frame is None:
				continue
			return_key, encoded_image = cv2.imencode(".jpg", video_frame)
			if not return_key:
				continue
	
        	# Output image as a byte array
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')

@app.route('/select', methods=['GET', 'POST'])
def select():
    global area
    if request.method == 'POST':  
        area[0] = (int(request.form['x1']),int(request.form['y1']))
        area[1] = (int(request.form['x2']),int(request.form['y2']))
        area[2] = (int(request.form['x3']),int(request.form['y3']))
        area[3] = (int(request.form['x4']),int(request.form['y4']))
      
        return redirect(url_for('ACI'))
    return render_template('select.html')

@app.route("/ACI")
def ACI():
	return render_template('ACI.html')

@app.route("/config")
def config():
        return Response(encodeFrame(), mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':

    	process_thread = threading.Thread(target=captureFrames)
    	process_thread.daemon = True
    	process_thread.start()
    	serve(app,host = host, port = port)
    	

