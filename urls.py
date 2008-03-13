from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^login/$', 'django.contrib.auth.views.login'),
    # static media
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'/home/jsled/stuff/proj/brewlog/app/media'}),
    (r'^', include('brewlog.app.urls')),
)
