flask-video-streaming
=====================

Supporting code for my article [video streaming with Flask](http://blog.miguelgrinberg.com/post/video-streaming-with-flask) and its follow-up [Flask Video Streaming Revisited](http://blog.miguelgrinberg.com/post/flask-video-streaming-revisited).


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

Set the `CAMERA` environment variable to use the pi
```
$ export CAMERA=pi
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