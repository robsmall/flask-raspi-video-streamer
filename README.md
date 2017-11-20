flask-raspi-video-streamer
==========================

Flask-RESTful API to create and serve up a live-stream from a raspberry pi to web and android clients.

Original code borrowed/altered from [miguelgrinberg/flask-video-streaming](https://github.com/miguelgrinberg/flask-video-streaming).

Set Up A Virtual Environment To Run The App Using Virtualenv On A Pi
--------------------------------------------------------------------

Install virtualenv on the pi as root
```
$ sudo pip install virtualenv
```

Then, create a `.env` virtual environment
```
$ virtualenv .env
```
and use it
```
$ source .env/bin/activate
```

Then, install all the requirements for the pi
```
$ pip install -U -r requirements-pi.txt
```

Set the `CAMERA` environment variable to use the pi camera for android
```
$ export CAMERA=pi_android
```

Now you are good to run the app using
```
$ python app.py
```


To Run Using Gunicorn
---------------------
Instead of running the app directly using python, run
```
$ gunicorn --threads 5 --workers 1 --bind 0.0.0.0:5000 app:app
```


Resources
---------
- [miguelgrinberg/flask-video-streaming](https://github.com/miguelgrinberg/flask-video-streaming)
    - Also see linked articles in repo's README
- [PiCamera Python Docs](http://picamera.readthedocs.io/en/latest)
    - [Web Streaming Example](http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming)


TODO
----
- This is currently set up for `pi_android`, hook everything else up to work properly too.
- Get this to work with web clients or allow for running of the one-off `simple_mjpeg-server.py` script.
- See TODOs in `video_feed.py`