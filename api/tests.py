from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from api.models import Project, Location
from django.contrib.auth import authenticate


class ProjectTestCase(TestCase):
	def setUp(self):
		self.client = Client()
	
	def test_create_project(self):
		response = self.client.post('/projects/', {'name':'tomate', 'description':'tomatensalat'})
		self.assertEqual(response.status_code, 201)
		project = Project.objects.get(name='tomate')
		self.assertEqual(project.name, 'tomate')
		self.assertEqual(project.description, 'tomatensalat')

	def test_get_project(self):
		Project.create(name='tomate', description='tomatensalat', url='hallo')
		response = self.client.get('/tomate/')
		self.assertEqual(response.status_code, 200)
		data = response.content.decode('utf-8')
		self.assertJSONEqual(data, {'name':'tomate', 'description':'tomatensalat'})		

	def test_update_project(self):
		Project.create(name='tomate', description='sdfgh sdfgjk', url='hallo')
		response = self.client.post('/tomate/', {'description':'tomatensalat'})
		self.assertEqual(response.status_code, 200)
		project = Project.objects.get(name='tomate')
		self.assertEqual(project.description, 'tomatensalat')
		self.assertEqual(project.url, 'hallo')

	def test_delete_project(self):
		Project.create(name='tomate', description='sdfgh sdfgjk', url='hallo')
		response = self.client.delete('/tomate/')
		self.assertEqual(response.status_code, 200)
		project = Project.objects.filter(name='tomate')
		self.assertEqual(len(project), 0)


class LocationTestCase(TestCase):
	def setUp(self):
		self.client = Client()

	def test_create_location(self):
		Project.create(name='tomate', description='tomatensalat', url='hallo')
		response = self.client.post('/tomate/locations/', {'title':'funfunfun', 'description':'nochmehrfun', 'lat':'0.0', 'lng':'0.0'})
		self.assertEqual(response.status_code, 201)
		location = Location.objects.get(title='funfunfun')
		self.assertEqual(location.title, 'funfunfun')
		self.assertEqual(location.description, 'nochmehrfun')

	def test_get_location(self):
		project = Project.create(name='tomate', description='tomatensalat', url='hallo')
		Location.create(title='funfunfun', lat=0.0, lng=0.0, description='nochmehrfun', project=project)
		response = self.client.get('/tomate/funfunfun/')
		self.assertEqual(response.status_code, 200)
		data = response.content.decode('utf-8')
		self.assertJSONEqual(data, {'title':'funfunfun', 'description':'nochmehrfun', 'lat':0.0, 'lng':0.0})

	def test_update_location(self):
		project = Project.create(name='tomate', description='tomatensalat', url='hallo')
		Location.create(title='funfunfun', lat=0.0, lng=0.0, description='nochmehrfun', project=project)
		response = self.client.post('/tomate/funfunfun/', {'description':'wenigerfunohhhh'})
		self.assertEqual(response.status_code, 200)
		location = Location.objects.get(title='funfunfun')
		self.assertEqual(location.description, 'wenigerfunohhhh')

	def test_delete_location(self):
		project = Project.create(name='tomate', description='tomatensalat', url='hallo')
		Location.create(title='funfunfun', lat=0.0, lng=0.0, description='nochmehrfun', project=project)
		response = self.client.delete('/tomate/funfunfun/')
		self.assertEqual(response.status_code, 200)
		location = Location.objects.filter(title='funfunfun')
		self.assertEqual(len(location), 0)

	def test_index_location(self):
		project = Project.create(name='tomate', description='tomatensalat', url='hallo')
		Location.create(title='funfunfun', lat=0.0, lng=0.0, description='nochmehrfun', project=project)
		Location.create(title='hasshasshass', lat=0.0, lng=0.0, description='nochmehrfun', project=project)
		response = self.client.get('/tomate/locations/')
		self.assertEqual(response.status_code, 200)
		data = response.content.decode('utf-8')
		self.assertJSONEqual(data, [{'description':'nochmehrfun', 'lat':0.0, 'title':'funfunfun', 'lng':0.0}, {'description':'nochmehrfun', 'lat':0.0, 'title':'hasshasshass', 'lng':0.0}])

	def test_valid_location(self):
		Project.create(name='tomate', description='tomatensalat', url='hallo')
		response = self.client.post('/tomate/locations/', {'title':'', 'description':'', 'lat':'', 'lng':''})
		self.assertEqual(response.status_code, 400)
		data = response.content.decode('utf-8')
		self.assertJSONEqual(data, {'title':['This field cannot be blank.'], 'lat':['\'\' value must be a float.'], 'lng':['\'\' value must be a float.']})

class StaticPagesTestCase(TestCase):
	def setUp(self):
		self.client = Client()

	def test_get_home(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)



class UserTestCase(TestCase):
	def setUp(self):
		self.client = Client()

	def test_create_user(self):
		response = self.client.post('/users/', {'username':'john', 'password':'tomaten', 'email':'john@example.com'})
		self.assertEqual(response.status_code, 201)
		user = User.objects.get(username='john')
		self.assertEqual(user.email, 'john@example.com')
		self.assertEqual(user.check_password('tomaten'), True)

	def test_create_invalid_user(self):
		response = self.client.post('/users/', {'username':'', 'password':'tomaten', 'email':'john@example.com'})
		self.assertEqual(response.status_code, 400)

	def test_delete_user(self):
		user = User.objects.create_user(username='hans', password='yoyoyo')
		response = self.client.delete('/profile/?username=hans')
		self.assertEqual(response.status_code, 200)
		user = User.objects.filter(username='hans')
		self.assertEqual(len(user), 0)

	def test_update_user(self):
		user = User.objects.create_user(username='hans', password='yoyoyo')
		response = self.client.post('/profile/?username=hans', {'password':'nonono'})
		self.assertEqual(response.status_code, 200)
		user = User.objects.get(username='hans')
		self.assertEqual(user.check_password('nonono'), True)

	def test_get_user(self):
		user = User.objects.create_user(username='hans', password='yoyoyo', email='hans@example.com')
		response = self.client.get('/profile/?username=hans')
		self.assertEqual(response.status_code, 200)
		data = response.content.decode('utf-8')
		self.assertJSONEqual(data, {'email':'hans@example.com'})





