# -*- coding: UTF-8 -*-

from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext

class AjaxMessage(HttpResponse):
	def __init__(self, type, code, message, data = None):
		ajax_message_as_json = {
			'type': type,
			'code': code,
			'message': message
		}
		if data:
			ajax_message_as_json['data'] = data
		HttpResponse.__init__(self, simplejson.dumps(ajax_message_as_json))

class AjaxSuccessMessage(AjaxMessage):
	def __init__(self, message = 'OK', data = None):
		AjaxMessage.__init__(self, 'success', 'ok', message, data = data)

class AjaxFailureMessage(AjaxMessage):
	def __init__(self, code, message, data = None):
		AjaxMessage.__init__(self, 'failure', code, message, data)

	@staticmethod
	def auto_render(code, message, request = None, data = None):
		'''
			Automatically select best way to render message: if this is AJAX
			request (request parameter is None), it returns JSON; if not
			(request parameter is HttpRequest object) - it renders html.
		'''

		if request:
			rdata = {
				'messages': [message]
			}
			return render_to_response('common/error.html', rdata, \
				context_instance=RequestContext(request))
		else:
			return AjaxFailureMessage(code, message, data)