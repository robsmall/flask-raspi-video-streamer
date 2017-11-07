#!/usr/bin/env python
from __future__ import print_function

import os
import sys
from importlib import import_module
from flask import Response
from flask import stream_with_context
from flask_restful import Resource
from flask_restful import reqparse

from base import BaseHandler


# Import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
    # TODO: lets remove everything but the android camera one... or duplicate
    # functionality and remove code
    CAMERA_MAP = import_module('camera_' + os.environ['CAMERA']).CAMERA_MAP
else:
    from camera import Camera
    from camera import CAMERA_MAP


# TODO: wrapper function to set the uid
# TODO: make sure we block this for everyone, until a user hits a StartFeedHandler.
#       start feed needs to be from the same user
class StopFeedHandler(BaseHandler):
    """
    Handler to stop the feed for all cameras.
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('uid', type=str)

    def post(self):
        args = self.parser.parse_args()
        self.uid = args.get('uid', None)

        print("Stop feed called from user: {}".format(self.uid))

        self.stop_all_cameras()

        params = {}

        return self.success_response(params)

    def stop_all_cameras(self):
        for uid, camera in CAMERA_MAP.iteritems():
            print("Closing camera for user: {}".format(self.uid))
            camera.close()


# TODO: wrapper function to set the uid
class VideoFeedHandler(BaseHandler):
    """
    Handler to start the feed for a camera and add the camera to the
    CAMERA_MAP.
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('uid', type=str)

    def get(self):
        args = self.parser.parse_args()
        self.uid = args.get('uid', None)

        # print("uid = {}".format(uid), file=sys.stderr)
        print("uid = {}".format(self.uid))

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
        camera = Camera(self.uid)

        return Response(response=stream_with_context(self.generate_frame(camera)),
                        status=200,
                        mimetype='multipart/x-mixed-replace; boundary=frame')
