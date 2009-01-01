from django.conf.urls.defaults import *
from django.contrib import admin

handler404 = 'brewjournal.app.views.custom_404'
handler500 = 'brewjournal.app.views.custom_500'

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/(.*)', admin.site.root),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'app/media'}),
    (r'^', include('brewjournal.app.urls')),
)
