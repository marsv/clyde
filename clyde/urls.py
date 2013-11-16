from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'clyde.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'api.views.home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/$', 'api.views.user_create'),
    url(r'^profile/$', 'api.views.user'),
	    










    url(r'^projects/$', 'api.views.project_create'),
    url(r'^(?P<slug>\w+)/$', 'api.views.project'),
    url(r'^(?P<slug>\w+)/locations/$', 'api.views.location_index_create'),
    url(r'^(?P<slug>\w+)/(?P<snail>\w+)/$', 'api.views.location'),
)
