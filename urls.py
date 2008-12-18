from django.conf.urls.defaults import *

handler404 = 'app.views.custom_404'

handler500 = 'app.views.custom_500'

urlpatterns = patterns(
    '',
    (r'^admin/', include('django.contrib.admin.urls')),
    # static media
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'/home/jsled/stuff/proj/brewjournal/app/media'}),
    (r'^', include('brewjournal.app.urls')),
)
