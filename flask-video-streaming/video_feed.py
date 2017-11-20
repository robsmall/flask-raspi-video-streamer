#!/usr/bin/env python
from __future__ import print_function

import os
import sys
from importlib import import_module
from flask import Response
from flask import stream_with_context
from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import inputs
from picamera import PiCameraNotRecording

from base import BaseHandler

# Import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
    USER_STOP_LIST = import_module('camera_' + os.environ['CAMERA']).USER_STOP_LIST
else:
    from camera import Camera
    from camera import USER_STOP_LIST


"""
TODOS:
    - Add a security layer. Probably an authN scheme to view the feed.
    - Wrapper function to get and set the uid
    - Error return wrapper
    - Log datetime.datetime.now with all logs and wrap it in a function
    - See TODO in generate_frame()
    - Deal with coming back after camera was destroyed when the camera is
      disabled client side
    - Add start and stop recording functionality to other cameras than
      camera_pi_android
    - Only allow disable/enable if uid is set. Maybe even only if the UID
      is in a map that we create when you ask for access
"""


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
        camera listeners if the current user is the only blocking user.
        """
        if self.uid in USER_STOP_LIST:
            USER_STOP_LIST.remove(self.uid)
            print('\nUser Stop List: {}\n'.format(USER_STOP_LIST))

            if not USER_STOP_LIST:
                Camera.start_recording()
            

class DisableFeedHandler(BaseHandler):
    """
    Handler to disable the feed for all camera listeners.
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('uid', type=str)

    def post(self):
        args = self.parser.parse_args()
        self.uid = args.get('uid', None)

        print("Disable feed called from user: {}".format(self.uid))

        self.disable_camera()

        params = {
            "blocking_cameras": len(USER_STOP_LIST),
        }

        return self.success_response(params)

    def disable_camera(self):
        USER_STOP_LIST.add(self.uid)

        print('\nUser Stop List: {}\n'.format(USER_STOP_LIST))

        try:
            Camera.stop_recording()
        except PiCameraNotRecording as e:
            print("Camera is not currently recording. Doing nothing...")


class VideoFeedHandler(BaseHandler):
    """
    Handler to start the feed for the camera and add the given user to the
    USER_LIST.
    """
    headers = {
        'Age': 0,
        'Cache-Control': 'no-cache, private',
        'Pragma': 'no-cache',
        'Content-Type': 'multipart/x-mixed-replace; boundary=frame',
    }

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('uid', type=str)
        self.parser.add_argument('is_mobile', type=inputs.boolean, default=False)

    def get(self):
        args = self.parser.parse_args()
        self.uid = args.get('uid', None)
        self.is_mobile = args.get('is_mobile')

        print("uid: {}".format(self.uid))
        print("is_mobile: {}".format(self.is_mobile))

        return self.video_feed()

    def generate_frame(self, camera):
        """ Video streaming generator function. """
        while True:
            frame = camera.get_frame()

            wrapped_frame = (b'--frame\r\n' +
                             b'Content-Type: image/jpeg\r\n\r\n')

            # TODO: figure out the difference here and why it is needed...
            #       for some reason, web can't handle this...
            if self.is_mobile:
               wrapped_frame += b'Content-Length: {}\r\n\r\n'.format(len(frame))

            wrapped_frame += frame + b'\r\n'

            yield wrapped_frame

    def video_feed(self):
        """
        Video streaming route. Put this in the src attribute of an img tag.
        """
        return Response(response=stream_with_context(
                            self.generate_frame(Camera())),
                        mimetype=self.headers['Content-Type'],
                        headers=self.headers,
                        status=200,
                        )
