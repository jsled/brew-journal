from django.conf.urls.defaults import *

# 2008-12-17, jsled: for dreamhost, these want to be 'brewjournal.app.[...]', but locally we want just "app.[...]".  :(
handler404 = 'brewjournal.app.views.custom_404'
handler500 = 'brewjournal.app.views.custom_500'

urlpatterns = patterns(
    '',
    (r'^admin/', include('django.contrib.admin.urls')),
    # static media
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'app/media'}),
    (r'^', include('brewjournal.app.urls')),
)
