#!/usr/bin/env python
import functools
import datetime

from flask import request
from flask_restful import Resource


class BaseHandler(Resource):
    def success_response(self, response):
        wrapped_response = {
            'status': 'SUCCESS',
            'response': response,
        }
        return wrapped_response

    def log_message(self, message, **kwargs):
        """
        Print the message with all kwargs appended.
        """
        kwargs = self._add_log_metadata(kwargs)
        print(message + ' ' +
              ', '.join(['{}={!r}'.format(k, v) for k, v in kwargs.iteritems()]))

    def _add_log_metadata(self, kwargs):
        """
        Add important metadata to the kwargs to be logged.
        """
        uid = getattr(self, 'uid', None)
        if uid:
            kwargs['uid'] = uid
        
        ipaddr = getattr(self, 'ipaddr', None)
        if ipaddr:
            kwargs['ipaddr'] = ipaddr

        kwargs['ts'] = datetime.datetime.now().isoformat()

        return kwargs


def set_args(method):
    """
    Decorator to set the following from the incoming request:
        self.args
        self.ipaddr
        self.uid
    """
    @functools.wraps(method)
    def decorated(self, *args, **kwargs):
        self.args = self.parser.parse_args()
        self.ipaddr = request.remote_addr
        self.uid = self.args.get('uid', None)
        return method(self, *args, **kwargs)
    return decorated