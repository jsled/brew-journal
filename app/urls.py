from django.conf.urls.defaults import *

urlpatterns = patterns(
    'app.views',
    (r'^$', 'root'),
    (r'^logout/$', 'logout_view'),
    # @fixme: new-user stuff
    (r'^user/(?P<user_name>[^/]+)/?$', 'user_index'),
    (r'^user/(?P<user_name>[^/]+)/profile/?$', 'user_profile'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)(/step/(?P<step_id>\d+))?/?$', 'brew'),
    (r'^user/(?P<user_name>[^/]+)/brew/new/?$', 'new_brew'),
)
