# Copyright (c) 2008-2010, Joshua Sled <jsled@asynchronous.org>
# See LICENSE file for "New BSD" license details.

from django.conf.urls import *
from app.feeds import NewUsers, NewRecipes

urlpatterns = patterns(
    'app.views',
    (r'^$', 'root'),

    (r'^logout/$', 'logout_view'),

    (r'^user/(?P<user_name>[^/]+)/?$', 'user_index'),
    (r'^user/(?P<user_name>[^/]+)/history/?$', 'user_history'),
    (r'^user/(?P<user_name>[^/]+)/profile/?$', 'user_profile'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)/?$', 'brew', {}, 'brew_url'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)/step/(?P<step_id>\d+)/?$', 'brew', {}, 'brew_step_url'),
    # /user/jsled/brew/new/?recipe_id=42
    (r'^user/(?P<user_name>[^/]+)/brew/new/?$', 'user_brew_new'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)/edit/$', 'brew_edit'),

    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)/competition-results/(?P<results_id>new|\d+)$', 'brew_edit_competition_results', {}, 'brew_comp_results_url'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)/competition-results/(?P<results_id>\d+)/delete$', 'brew_delete_competition_results'),

    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)/competition-results/(?P<results_id>\d+)/scoresheet/(?P<scoresheet_id>new|\d+)$', 'brew_edit_comp_scoresheet', {}, 'brew_comp_scoresheet_url'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)/competition-results/(?P<results_id>\d+)/scoresheet/(?P<scoresheet_id>\d+)/delete$', 'brew_delete_comp_scoresheet'),

    (r'^user/(?P<user_name>[^/]+)/shopping/?$', 'user_shopping_list'),

    # /recipe/new/?clone_from_recipe_id=42
    # /recipe/new/?clone_from_url=<...>
    (r'^recipe/new/$', 'recipe_new'),
    (r'^recipe/(?P<recipe_id>\d+)/(?P<recipe_name>.+)?$', 'recipe', {}, 'recipe_url'),
    (r'^recipe/$', 'recipe_index'),

    (r'^calc/mash-sparge/$', 'calc_mash_sparge'),

    (r'^hops', 'hops'),

    (r'^feeds/new-users$', NewUsers()),
    (R'^feeds/new-recipes$', NewRecipes()),

    (r'^500$', 'intentional_500'),
)
