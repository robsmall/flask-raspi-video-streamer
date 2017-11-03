import io
import time
import picamera
from base_camera import BaseCamera
# from threading import Condition

# Taken from picamera.readthedocs.io section 4.10
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        # self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            # with self.condition:
            self.frame = self.buffer.getvalue()
                # self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class Camera(BaseCamera):
    @staticmethod
    def frames():
        with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
            # # let camera warm up
            # time.sleep(2)

            # stream = StreamingOutput ()
            # for foo in camera.capture_continuous(stream, 'jpeg',
            #                                      use_video_port=True):
            #     # return current frame
            #     stream.seek(0)
            #     yield stream.read()

            #     # reset stream for next frame
            #     stream.seek(0)
            #     stream.truncate()
            output = StreamingOutput()
            camera.start_recording(output, format='mjpeg')
            try:
                while True:
                    # with output.condition:
                        # output.condition.wait()
                    frame = output.frame
                    yield frame
                    # self.wfile.write(b'--FRAME\r\n')
                    # self.send_header('Content-Type', 'image/jpeg')
                    # self.send_header('Content-Length', len(frame))
                    # self.end_headers()
                    # self.wfile.write(frame)
                    # self.wfile.write(b'\r\n')
            except Exception as e:
                print('Removed streaming client {0}: {1}'.format(
                      self.client_address, str(e)))