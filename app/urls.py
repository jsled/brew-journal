# Copyright (c) 2008-2009, Joshua Sled <jsled@asynchronous.org>
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
# 
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
# 
#     * The names of its contributors may not be used to endorse or promote
#       products derived from this software without specific prior written
#       permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from django.conf.urls.defaults import *

urlpatterns = patterns(
    'brewjournal.app.views',
    (r'^$', 'root'),
    (r'^logout/$', 'logout_view'),
    (r'^user/(?P<user_name>[^/]+)/?$', 'user_index'),
    (r'^user/(?P<user_name>[^/]+)/profile/?$', 'user_profile'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)(/step/(?P<step_id>\d+))?/?$', 'brew'),
    # /user/jsled/brew/new/?recipe_id=42
    (r'^user/(?P<user_name>[^/]+)/brew/new/?$', 'user_brew_new'),
    (r'^user/(?P<user_name>[^/]+)/brew/(?P<brew_id>\d+)/edit/$', 'brew_edit'),

    (r'^user/(?P<user_name>[^/]+)/shopping/?$', 'user_shopping_list'),

    # GET /user/jsled/star?recipe_id=42 + POST
    # GET /user/jsled/star?url=<http://.../recipe> + POST
    (r'^user/(?P<user_name>[^/]+)/star/$', 'user_star'),
    
    # /recipe/new/?clone_from_recipe_id=42
    # /recipe/new/?clone_from_url=<...>
    (r'^recipe/new/$', 'recipe_new'),
    (r'^recipe/(?P<recipe_id>\d+)/grain/$', 'recipe_grain'),
    (r'^recipe/(?P<recipe_id>\d+)/hop/$', 'recipe_hop'),
    (r'^recipe/(?P<recipe_id>\d+)/adjunct/$', 'recipe_adjunct'),
    (r'^recipe/(?P<recipe_id>\d+)/yeast/$', 'recipe_yeast'),

    (r'^recipe/(?P<recipe_id>\d+)/(?P<recipe_name>.+)?$', 'recipe'),
)
