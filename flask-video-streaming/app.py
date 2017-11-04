#!/usr/bin/env python
from importlib import import_module
from flask import Flask, render_template, Response, request, abort, stream_with_context
from flask_restful import Resource, Api
import video_feed

app = Flask(__name__)
api = Api(app)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


@app.route('/stop_feed', methods=['POST'])
def stop_feed():
    if request.method == 'POST':
        pass
    else:
        abort(403)


# Add handlers.
api.add_resource(video_feed.VideoFeedHandler, '/video_feed')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
