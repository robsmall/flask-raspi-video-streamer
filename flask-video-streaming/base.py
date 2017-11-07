#!/usr/bin/env python
from flask_restful import Resource


class BaseHandler(Resource):
    def success_response(self, response):
        wrapped_response = {
            'status': 'SUCCESS',
            'response': response,
        }
        return wrapped_response