from django.conf.urls.defaults import *

urlpatterns = patterns(
    'app.views',
    (r'^$', 'root'),
    (r'^logout/$', 'logout_view'),
    (r'^user/(?P<user_name>[^/]+)/?$', 'user_index'),
    (r'^user/(?P<user_name>[^/]+)/profile/?$', 'user_profile'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)(/step/(?P<step_id>\d+))?/?$', 'brew'),
    # /user/jsled/brew/new/?recipe=42
    (r'^user/(?P<user_name>[^/]+)/brew/new/?$', 'new_brew'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)/edit/$', 'brew_edit'),

    (r'^user/(?P<user_name>[^/]+)/recipe/$', 'user_recipe_index'),

    # GET /user/jsled/star?recipe_id=42 + POST
    # GET /user/jsled/star?url=<http://.../recipe> + POST
    # (r'^user/(?P<user_name>[^/]+)/recipe/star/$', 'user_recipe_star'),
    
    # /recipe/new/?clone_from_recipe_id=42
    # /recipe/new/?clone_from_url=<...>
    (r'^recipe/new/$', 'recipe_new'),
    (r'^recipe/((?P<recipe_id>\d+)/)?$', 'recipe'),
    (r'^recipe/(?P<recipe_id>\d+)/grain/$', 'recipe_grain'),
    (r'^recipe/(?P<recipe_id>\d+)/hop/$', 'recipe_hop'),
    (r'^recipe/(?P<recipe_id>\d+)/adjunct/$', 'recipe_adjunct'),
    (r'^recipe/(?P<recipe_id>\d+)/yeast/$', 'recipe_yeast'),
)
