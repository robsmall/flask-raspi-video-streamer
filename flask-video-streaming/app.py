#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# For explicitly using the pi camera
# from camera_pi import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        # yield (b'--frame\r\n'
        #       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        yield (b'Age: {}'.format(0) +
               b'Cache-Control: no-cache, private' +
               b'Pragma: no-cache' +
               b'Content-Type: multipart/x-mixed-replace; boundary=FRAME' +
               b'--FRAME\r\n' +
               b'Content-Type: image/jpeg\r\n\r\n' +
               b'Content-Length: {}\r\n\r\n'.format(len(frame)) +
               frame +
               b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
                        # self.wfile.write(b'--FRAME\r\n')
                    # self.send_header('Content-Type', 'image/jpeg')
                    # self.send_header('Content-Length', len(frame))
                    # self.end_headers()
                    # self.wfile.write(frame)
                    # self.wfile.write(b'\r\n')
    return Response(gen(Camera()),
                    # content_type='image/jpeg'
                    # headers=['Content-Type', 'image/jpg'
                    #          'Content-length']
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
