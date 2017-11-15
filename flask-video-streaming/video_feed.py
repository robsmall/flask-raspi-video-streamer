#!/usr/bin/env python
from __future__ import print_function

import os
import sys
from importlib import import_module
from flask import Response
from flask import stream_with_context
from flask_restful import Resource
from flask_restful import reqparse
from picamera import PiCameraNotRecording

from base import BaseHandler

# Import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
    # TODO: lets remove everything but the android camera one... or duplicate
    # functionality and remove code
    CAMERA_MAP = import_module('camera_' + os.environ['CAMERA']).CAMERA_MAP
    USER_STOP_LIST = import_module('camera_' + os.environ['CAMERA']).USER_STOP_LIST
else:
    from camera import Camera
    from camera import CAMERA_MAP
    from camera import USER_STOP_LIST

'''
TODOS:
    - Wrapper function to get and set the uid
    - Error return wrapper
    - Log datetime.datetime.now with all logs and wrap it in a function
'''

class EnableFeedHandler(BaseHandler):
    """
    Handler to enable the feed for all cameras.

    Note: If another user is also disabling all feeds, then the feed will not
          be enabled until all users re-enable.
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('uid', type=str)

    def post(self):
        args = self.parser.parse_args()
        self.uid = args.get('uid', None)

        print("Enable feed called from user: {}".format(self.uid))

        self.enable_cameras()

        params = {
            "blocking_cameras": len(USER_STOP_LIST),
        }

        return self.success_response(params)

    def enable_cameras(self):
        """
        Remove the current user's uid from the USER_STOP_LIST and enable all
        cameras in the CAMERA_MAP if the current user is the only blocking user.
        """
        if self.uid in USER_STOP_LIST:
            USER_STOP_LIST.remove(self.uid)
            print('\nUser Stop List: {}\n'.format(USER_STOP_LIST))

            if not USER_STOP_LIST:
                for uid, camera in CAMERA_MAP.iteritems():
                    print("Enabling camera for user: {}".format(self.uid))
                    camera.camera.start_recording(camera.output, format='mjpeg')
            

class DisableFeedHandler(BaseHandler):
    """
    Handler to disable the feed for all cameras.
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('uid', type=str)

    def post(self):
        args = self.parser.parse_args()
        self.uid = args.get('uid', None)

        print("Disable feed called from user: {}".format(self.uid))

        self.disable_cameras()

        params = {
            "blocking_cameras": len(USER_STOP_LIST),
        }

        return self.success_response(params)

    def disable_cameras(self):
        USER_STOP_LIST.add(self.uid)

        print('\nUser Stop List: {}\n'.format(USER_STOP_LIST))
        for uid, camera in CAMERA_MAP.iteritems():
            print("Closing camera for user: {}".format(self.uid))
            try:
                camera.camera.stop_recording()
            except PiCameraNotRecording as e:
                print("Camera is not currently recording: {}".format(uid))


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
