from django.conf.urls import patterns, include, url
from api.views import RegistrationView, LoginView, ProjectView, LocationView, UserView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'clyde.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'api.views.home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/$', RegistrationView.as_view()),
    url(r'^users/login/$', LoginView.as_view()),
    url(r'^profile/$', UserView.as_view()),
	url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),



    url(r'^projects/$', ProjectView.as_view()),
    url(r'^(?P<slug>\w+)/$', ProjectView.as_view()),
    url(r'^(?P<slug>\w+)/locations/$', LocationView.as_view()),
    url(r'^(?P<slug>\w+)/(?P<snail>\w+)/$', LocationView.as_view()),
)
