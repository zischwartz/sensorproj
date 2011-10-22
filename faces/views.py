# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from models import *
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime

from django.views.generic import ListView, DetailView

import logging
import settings



def getlogger():
    logger = logging.getLogger()
    hdlr = logging.FileHandler(settings.LOG_FILE)
    formatter = logging.Formatter('[%(asctime)s]%(levelname)-8s"%(message)s"','%Y-%m-%d %a %H:%M:%S') 
    
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    return logger

def info(msg):
    logger = getlogger()
    logger.info(msg)

logger=getlogger()





def Home (request): 
	logger.info('Home...!')
	# Face.objects

	return HttpResponse('hi')
	
def NewFace (request): 
	logger.info('newface view')

	if request.method == 'GET':
		return HttpResponse("<form method='post' enctype='multipart/form-data'><input type='file' name='file' /><input type='submit' name='submit' value='Upload' /></form>")
	
	if request.method == 'POST':		
		if 'file' in request.FILES:
			file = request.FILES['file']
			filename = file.name
			logger.info(filename)

			face = Face(name=file.name, file=file)

			face.save()
			return HttpResponse(filename+' uploaded!')

		else:
			return HttpResponse('No file sent.')
	# f = request.FILES.get('file')
	# if f:
		# return HttpResponse('newface : ' + f +'<br>' + request.method)
	# else:
		# return HttpResponse('no face file found')










logger.info("---------------")