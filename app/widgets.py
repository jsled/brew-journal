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

from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django import forms

def flatatt(attrs):
    """
    Convert a dictionary of attributes to a single string.
    The returned string will contain a leading space followed by key="value",
    XML-style pairs.  It is assumed that the keys do not need to be XML-escaped.
    If the passed dictionary is empty, then return an empty string.
    jsled: stolen from django newforms/util.py...
    """
    return u''.join([u' %s="%s"' % (k, escape(v)) for k, v in attrs.items()])


class TwoLevelSelectWidget (forms.Widget):
    def __init__(self, attrs=None, choices=()):
        super(TwoLevelSelectWidget, self).__init__(attrs)
        self._choices = list(choices)

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select%s>' % flatatt(final_attrs)]
        str_value = force_unicode(value)
        for top_label,subs in self._choices:
            output.append(u'<optgroup label="%s">' % (conditional_escape(force_unicode(top_label))))
            for opt_value,opt_label in subs:
                opt_value = force_unicode(opt_value)
                selected_html = (opt_value == str_value) and u' selected="selected"' or ''
                output.append(u'<option value="%s"%s>%s</option>' % (escape(opt_value), selected_html,
                                                                     conditional_escape(force_unicode(opt_label))))
            output.append(u'</optgroup>')
        output.append(u'</select>')
        return mark_safe(u'\n'.join(output))
        

