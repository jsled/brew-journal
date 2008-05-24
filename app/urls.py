from django.conf.urls.defaults import *

urlpatterns = patterns(
    'app.views',
    (r'^$', 'root'),
    (r'^logout/$', 'logout_view'),
    (r'^user/(?P<user_name>[^/]+)/?$', 'user_index'),
    (r'^user/(?P<user_name>[^/]+)/profile/?$', 'user_profile'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)(/step/(?P<step_id>\d+))?/?$', 'brew'),
    (r'^user/(?P<user_name>[^/]+)/brew/new/?$', 'new_brew'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)/edit/$', 'brew_edit'),

    (r'^user/(?P<user_name>[^/]+)/recipe/$', 'user_recipe_index'),
    
    (r'^recipe/new/$', 'recipe_new'),
    (r'^recipe/((?P<recipe_id>\d+)/)?$', 'recipe'),
    (r'^recipe/(?P<recipe_id>\d+)/grain/$', 'recipe_grain'),
    (r'^recipe/(?P<recipe_id>\d+)/hop/$', 'recipe_hop'),
    (r'^recipe/(?P<recipe_id>\d+)/adjunct/$', 'recipe_adjunct'),
    (r'^recipe/(?P<recipe_id>\d+)/yeast/$', 'recipe_yeast'),
)
