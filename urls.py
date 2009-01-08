from django.conf.urls.defaults import *
from django.contrib import admin
from brewjournal.app.feeds import NewUsers

feeds = {
    'new-users': NewUsers
    }

handler404 = 'brewjournal.app.views.custom_404'
handler500 = 'brewjournal.app.views.custom_500'

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/(.*)', admin.site.root),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'app/media'}),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^', include('brewjournal.app.urls')),
)
