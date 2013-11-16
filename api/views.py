import json
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.contrib.auth.models import User
from api.helpers import unique_slugify
from api.models import Project
from api.models import Location
from django.contrib.auth import authenticate

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
		response.content = data
		
	elif request.method == r'DELETE':
		project.delete()

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
		lat = request.POST.get('lat', None)
		lng = request.POST.get('lng', None)
		description = request.POST.get('description','')
		title = request.POST.get('title','')
		img = request.POST.get('img', '')
		check = Location.create(project=project, title=title, description=description, lat=lat, lng=lng, img=img)
		if check == True:
			response.status_code = 201
		else:
			response.status_code = 400
			response.content = json.dumps(check.message_dict)
		
	elif request.method == 'GET':
		locations = Location.objects.filter(project=project)
		data = json.dumps([{'title':l.title, 'description':l.description, 'lat':l.lat, 'lng':l.lng} for l in locations])
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
		response.content = data
		
	elif request.method == r'DELETE':
		location.delete()

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

		unique_slugify(location, location.title) 
		location.save()
	
	return response


def user_create(request):
	response = HttpResponse("", content_type='application/json; charset=utf-8')
	if request.method == 'POST':
		username = request.POST.get('username','')
		email = request.POST.get('email','')
		password = request.POST.get('password','')
		# if username == None or email == None or password == None:
		# 	response.status_code = 400
		# 	return response

		try: 
			User.objects.create_user(username=username, email=email, password=password)
		except:
			response.status_code = 400
			return response
		response.status_code = 201
		return response

def user(request):
	response = HttpResponse("", content_type='application/json; charset=utf-8')
	username = request.GET.get('username','')
	user = User.objects.get(username=username)
	
	# if authenticate_user(username, password) == False:
	# 	response.status_code = 401
	# 	return response

	if request.method == r'DELETE':
		user.delete()
	elif request.method == 'POST':
		password = request.POST.get('password')
		user.set_password(password)
		user.full_clean()
		user.save()
	elif request.method == 'GET':
		data = json.dumps({'email':user.email})
		response.content = data
	return response

def authenticate_user(username, password):
	user = authenticate(username=username, password=password)
	if user is not None:
		# the password verified for the user
		if user.is_active:
			print("User is valid, active and authenticated")
		else:
			print("The password is valid, but the account has been disabled!")
		return True
	else:
		# the authentication system was unable to verify the username and password
		print("The username and password were incorrect.")
		return False
