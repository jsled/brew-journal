from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'^admin/', include('django.contrib.admin.urls')),
    # static media
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'/home/jsled/stuff/proj/brewjournal/app/media'}),
    (r'^', include('brewjournal.app.urls')),
)
