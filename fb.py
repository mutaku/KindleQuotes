#!/usr/bin/env python
#       Post to Facebook
# -*- coding: utf_8 -*-

import fbconsole

class FacebookIt():
    '''Post to Facebook using fbconsole.'''
    def __init__(self, app_id=None):
        if app_id:
            fbconsole.APP_ID = '<'+app_id+'>'

	fbconsole.AUTH_SCOPE = ['publish_stream', 'publish_checkins']
	fbconsole.authenticate()

    def post(self, data):
        result = fbconsole.post('/me/feed', {'message':data})
        
    def logout(self):
        fbconsole.logout()
