from django.contrib.syndication.feeds import Feed
from django.contrib.auth.models import User
from django.utils.feedgenerator import Atom1Feed

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
