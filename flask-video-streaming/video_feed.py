#!/usr/bin/env python
from __future__ import print_function

import os
import sys
from importlib import import_module
from flask import Response
from flask import stream_with_context
from flask_restful import Resource
from flask_restful import reqparse


# Import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

camera_map = {}


class VideoFeedHandler(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('uid', type=str)

    def get(self):
        args = self.parser.parse_args()
        uid = args.get('uid', None)

        # print("uid = {}".format(uid), file=sys.stderr)
        print("uid = {}".format(uid))

        return self.video_feed()

    def generate_frame(self, camera):
        """ Video streaming generator function. """
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

    def video_feed(self):
        """Video streaming route. Put this in the src attribute of an img tag."""
        # self.wfile.write(b'--FRAME\r\n')
        # self.send_header('Content-Type', 'image/jpeg')
        # self.send_header('Content-Length', len(frame))
        # self.end_headers()
        # self.wfile.write(frame)
        # self.wfile.write(b'\r\n')
        camera = Camera()
        return Response(response=stream_with_context(self.generate_frame(camera)),
                        status=200,
                        mimetype='multipart/x-mixed-replace; boundary=frame')
