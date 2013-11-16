from django.db import models
from api.helpers import unique_slugify

# Create your models here.

class Image(models.Model):
	url = models.URLField()


class Project(models.Model):
	name = models.CharField(max_length=200)
	slug = models.SlugField()
	description = models.TextField(default='')
	url = models.URLField(default='')
	img = models.ForeignKey(Image, blank=True, null=True)

	def __unicode__(self):
		return self.name

	@classmethod
	def create(self, name, description, url, img):
		project = Project(name=name, description=description, url=url)
		unique_slugify(project, name)
		project.save()
		return project


class Location(models.Model):
	title = models.CharField(max_length=200)
	slug = models.SlugField()
	description = models.TextField(default='')
	lat = models.FloatField(default=0.0, db_index=True)
	lng = models.FloatField(default=0.0, db_index=True)
	images = models.ManyToManyField(Image, blank=True, null=True)
	project = models.ForeignKey(Project)

	def __unicode__(self):
		return self.title

	@classmethod
	def create(self, title, description, lat, lng, img, project):
		location = Location(title=title, description=description, lat=lat, lng=lng, project=project)
		unique_slugify(location, title)
		location.save()
		return location



