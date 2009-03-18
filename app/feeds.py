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
