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
from oauth2_provider.views.generic import ProtectedResourceView
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.decorators import protected_resource
from oauth2_provider.models import AccessToken
from django.views.generic import View
from django.http import HttpResponseForbidden


class Helper():
	@staticmethod
	def params(request):
		return json.loads(request.body.decode('utf-8'))

	@staticmethod
	def current_user(request):
		return AccessToken.objects.get(token=request.META['Authorization'].split()[1]).user

class RegistrationView(View):

	def post(self, request):
		request._set_post(json.loads(request.body.decode('utf-8')))

		params = Helper.params(request)
		
		username = params['username']
		email = params['email']
		password = params['password']
		# if username == None or email == None or password == None:
		# 	response.status_code = 400
		# 	return response
		try: 
			User.objects.create_user(username=username, email=email, password=password)
		except:
			response = HttpResponse("", content_type='application/json; charset=utf-8')
			response.status_code = 400
			return response

		url, headers, body, status = OAuthLibCore().create_token_response(request=request)
		response = HttpResponse(content=body, status=status, content_type='application/json; charset=utf-8')
		for k, v in headers.items():
			response[k] = v
		response.status_code = 201
		
		return response

class LoginView(View):
	def post(self, request):
		request._set_post(json.loads(request.body.decode('utf-8')))

		url, headers, body, status = OAuthLibCore().create_token_response(request=request)
		response = HttpResponse(content=body, status=status, content_type='application/json; charset=utf-8')
		for k, v in headers.items():
			response[k] = v
		response.status_code = 201
		return response

class ProjectView(ProtectedResourceView):
	def post(self, request):
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

	def get(self, request, slug):
		response = HttpResponse("", content_type='application/json; charset=utf-8')
		project = Project.objects.get(slug=slug)
		if project == None:
			response.status_code = 404
			return response
		data = json.dumps({'name':project.name, 'description':project.description})
		response.content = data
		return response

	def put(self, request, slug):
		response = HttpResponse("", content_type='application/json; charset=utf-8')
		project = Project.objects.get(slug=slug)
		params = Helper.params(request)

		project.description = params['description']
		try:
			value = params['url']
			value = params['img']
		except:
			pass
		
		project.save()
		unique_slugify(project, project.name)
		return response

	def delete(self, request, slug):
		response = HttpResponse("", content_type='application/json; charset=utf-8')
		project = Project.objects.get(slug=slug)
		project.delete()
		return response

class LocationView(ProtectedResourceView):
	def post(self, request, slug):
		response = HttpResponse("", content_type='application/json; charset=utf-8')
		project = Project.objects.get(slug=slug)
		if project == None:
			response.status_code = 404
			return response

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
		return response

	def get(self, request, slug, snail=None):
		if snail == None:
			return self.index(request, slug)
		else:
			return self.show(request, slug, snail)


	def index(self, request, slug):
		response = HttpResponse("", content_type='application/json; charset=utf-8')
		project = Project.objects.get(slug=slug)
		if project == None:
			response.status_code = 404
			return response

		locations = Location.objects.filter(project=project)
		data = json.dumps([{'title':l.title, 'description':l.description, 'lat':l.lat, 'lng':l.lng} for l in locations])
		response.content = data

		return response

	def show(self, request, slug, snail):
		response = HttpResponse("", content_type='application/json; charset=utf-8')
		project = Project.objects.get(slug=slug)
		location = Location.objects.get(slug=snail, project=project)
		if project == None:
			response.status_code = 404
			return response
		location = Location.objects.get(slug=snail, project=project)

		data = json.dumps({'title':location.title, 'description':location.description, 'lat':location.lat, 'lng':location.lng})
		response.content = data

		return response

	def put(self, request, slug, snail):
		response = HttpResponse("", content_type='application/json; charset=utf-8')
		project = Project.objects.get(slug=slug)
		if project == None:
			response.status_code = 404
			return response
		location = Location.objects.get(slug=snail, project=project)
		params = Helper.params(request)

		location.description = params['description']
		try:
			value = params['lat']
			value = params['lng']
			value = params['title']
		except:
			pass

		unique_slugify(location, location.title) 
		location.save()
		return response

	def delete(self, request, slug, snail):
		response = HttpResponse("", content_type='application/json; charset=utf-8')
		project = Project.objects.get(slug=slug)
		if project == None:
			response.status_code = 404
			return response
		location = Location.objects.get(slug=snail, project=project)
		location.delete()
		return response




def home(request):
	return render(request, 'index.html')


class UserView(ProtectedResourceView):
	response = HttpResponse("", content_type='application/json; charset=utf-8')
	user = None

	def setRequestEnv(self, request):
		self.user = User.objects.get(username=request.GET.get('username',''))

	def userAllowed(self, request):
		if request.method.lower() == 'delete':
			if self.user!=Helper.current_user(request):
				return False

		return True 

	def init(self, request):
		self.setRequestEnv(request)
		if not self.userAllowed(request): 
			return HttpResponseForbidden('')
		return None

	def get(self, request):	
		init = self.init(request)
		if init != None: 
			return init
			

		data = json.dumps({'email':self.user.email})
		self.response.content = data

		return self.response

	def post(self, request):
		init = self.init(request)
		if init != None:
			return init

		password = request.POST.get('password')
		self.user.set_password(password)
		self.user.full_clean()
		self.user.save()

		return self.response

	def delete(self, request):
		init = self.init(request)
		if init != None:
			return init

		if self.user==Helper.current_user(request):
			self.user.delete()
		else:
			self.response.status_code = 403

		return self.response
