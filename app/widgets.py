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
        output.append('u</select>')
        return mark_safe(u'\n'.join(output))
        

