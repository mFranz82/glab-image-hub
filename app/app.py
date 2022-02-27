from flask import Flask, render_template, Response, make_response
from urllib.request import urlopen
import numpy as np
import cv2
from datetime import datetime

app = Flask(__name__)

CAM_RIGHT_URL = os.environ['CAM_RIGHT_URL']
CAM_LEFT_URL = os.environ['CAM_LEFT_URL']

# Pre callculate the rectification maps with the given Calibration Results
# TODO Make this work with no fisheye cameras to
# TODO Use envs here (Image size, File Path)
K = np.genfromtxt('K.csv', delimiter=',')
D = np.genfromtxt('D.csv', delimiter=',')
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, (1600,1200), cv2.CV_16SC2)

def get_image(CAM):
    resp = urlopen(CAM)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    undistorted_image = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    cv2.putText(undistorted_image,str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),(20,40), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
    return undistorted_image

def gen_frames(CAM):  # generate frame by frame from camera
    while True:
        frame = get_image(CAM)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 


@app.route('/cam/right/stream')
def cam_right_stream():
    return Response(gen_frames(CAM_RIGHT_URL), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cam/left/stream')
def cam_left_stream():
    return Response(gen_frames(CAM_LEFT_URL), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cam/right/capture')
def cam_right_capture():
    image = get_image(CAM_RIGHT_URL)
    ret, buffer = cv2.imencode('.jpg', image)
    response = make_response(buffer.tobytes())
    response.headers['Content-Type'] = 'image/jpg'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)