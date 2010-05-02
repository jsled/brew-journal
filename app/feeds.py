# Copyright (c) 2008-2010, Joshua Sled <jsled@asynchronous.org>
# See LICENSE file for "New BSD" license details.

from django.contrib.syndication.feeds import Feed
from django.contrib.auth.models import User
from django.utils.feedgenerator import Atom1Feed
from brewjournal.app.models import Recipe

class UserItemWrapper (object):
    def __init__(self, user_item):
        self._user = user_item

    def __str__(self):
        return u'%(first)s %(last)s (%(username)s) @ %(date)s' % {'username': self._user.username,
                                                                  'first': self._user.first_name,
                                                                  'last': self._user.last_name,
                                                                  'date': self._user.date_joined.strftime('%Y-%m-%d %H:%M')}
    def __unicode__(self):
        return str(self)

    def get_absolute_url(self):
        return '/user/%s/' % (self._user.username)

class NewUsers (Feed):
    feed_type = Atom1Feed
    title = 'brew-journal new users'
    link = '/'

    def items(self):
        return [UserItemWrapper(x) for x in User.objects.order_by('-date_joined')[:50]]


class RecipeWrapper (object):
    def __init__(self, recipe_item):
        self._recipe = recipe_item

    def __unicode__(self):
        return u'%(name)s (%(style)s) @ %(date)s by %(username)s' \
               % {'name': self._recipe.name,
                  'style': (self._recipe.style and self._recipe.style.name) or u'unknown style',
                  'date': self._recipe.insert_date.strftime('%Y-%m-%d %H:%M'),
                  'username': self._recipe.author.username}

    def __str__(self):
        return self.__unicode__()

    def get_absolute_url(self):
        return self._recipe.url()


class NewRecipes (Feed):
    feed_type = Atom1Feed
    title = 'brew-journal new recipes'
    link = '/'

    def items(self):
        return [RecipeWrapper(x) for x in Recipe.objects.order_by('-insert_date')[:50]]
