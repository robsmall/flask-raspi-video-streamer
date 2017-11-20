import io
import time
import picamera
from base_camera import BaseCamera


USER_STOP_LIST = set()


# Taken from picamera.readthedocs.io section 4.10
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            self.frame = self.buffer.getvalue()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class Camera(BaseCamera):
    camera = None
    output = None

    @staticmethod
    def start_recording():
        """ Start recording from the camera object. """
        # Only start the camera if there are no users currently blocking
        # the camera. If there are, the feed will be started when they
        # re-enable the camera.
        if not USER_STOP_LIST:
            Camera.camera.start_recording(Camera.output, format='mjpeg')

    @staticmethod
    def stop_recording():
        """ Stop the Camera object from recording. """
        Camera.camera.stop_recording()

    @staticmethod
    def frames():
        with picamera.PiCamera(sensor_mode=5, resolution="1640x922", framerate=40) as camera:
            Camera.camera = camera
            Camera.output = StreamingOutput()

            Camera.start_recording()
            
            while True:
                # with self.output.condition:
                    # self.output.condition.wait()
                frame = Camera.output.frame
                yield frame
