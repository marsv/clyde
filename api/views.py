import json
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from api.helpers import unique_slugify
from api.models import Project
from api.models import Location


def home(request):
	return render(request, 'index.html')

def project_create(request):
	if request.method == 'POST':
		response = HttpResponse("", content_type='application/json; charset=utf-8')
		name = request.POST.get('name','')
		description = request.POST.get('description','')
		url = request.POST.get('url','')
		img = request.POST.get('img', '')
		if Project.create(name, description, url, img) != None:
			response.status_code = 201
		else:
			response.status_code = 400
		return response


def project(request, slug):
	response = HttpResponse("", content_type='application/json; charset=utf-8')
	project = Project.objects.get(slug=slug)
	if project == None:
		response.status_code = 404
		return response

	if request.method == 'GET':
		data = json.dumps({'name':project.name, 'description':project.description})
		response.status_code = 200
		response.content = data
		
	elif request.method == r'DELETE':
		project.delete()
		response.status_code = 200

	elif request.method == 'POST':
		value = request.POST.get('description',None)
		if value != None:
			project.description = value 
		value = request.POST.get('url',None)
		if value != None:
			project.url = value 
		value = request.POST.get('img', None)
		if value != None:
			project.img = value
		response.status_code = 200
		project.save()
		unique_slugify(project, project.name) 
	
	return response



def location_index_create(request, slug):
	response = HttpResponse("", content_type='application/json; charset=utf-8')
	project = Project.objects.get(slug=slug)
	if project == None:
		response.status_code = 404
		return response

	if request.method == 'POST':
		response = HttpResponse()
		lat = request.POST.get('lat', '0.0')
		lng = request.POST.get('lng', '0.0')
		description = request.POST.get('description','')
		title = request.POST.get('title','')
		img = request.POST.get('img', '')
		Location.create(project, title, description, lat, lng, img)
		response.status_code = 201
		
	elif request.method == 'GET':
		locations = Location.objects.filter(project=project)
		data = json.dumps([{'title':l.title, 'description':l.description, 'lat':l.lat, 'lng':l.lng} for l in locations])
		response.status_code = 200
		response.content = data

	return response

def location(request, slug, snail):
	response = HttpResponse("", content_type='application/json; charset=utf-8')
	project = Project.objects.get(slug=slug)
	location = Location.objects.get(slug=snail, project=project)
	if project == None or location == None:
		response.status_code = 404
		return response

	if request.method == 'GET':
		data = json.dumps({'title':location.title, 'description':location.description, 'lat':location.lat, 'lng':location.lng})
		response.status_code = 200
		response.content = data
		
	elif request.method == r'DELETE':
		location.delete()
		response.status_code = 200

	elif request.method == 'POST':
		value = request.POST.get('description',None)
		if value != None:
			location.description = value 
		value = request.POST.get('lat',None)
		if value != None:
			location.lat = value 
		value = request.POST.get('lng', None)
		if value != None:
			location.lng = value 
		value = request.POST.get('title', None)
		if value != None:
			location.title = value

		response.status_code = 200
		unique_slugify(location, location.title) 
		location.save()
	
	return response



