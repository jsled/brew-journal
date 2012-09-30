
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import os

# from http://www.djangosnippets.org/snippets/97/

app_dirs = []
for app in settings.INSTALLED_APPS:
    i = app.rfind('.')
    if i == -1:
        m, a = app, None
    else:
        m, a = app[:i], app[i+1:]
    try:
        if a is None:
            mod = __import__(m, {}, {}, [])
        else:
            mod = getattr(__import__(m, {}, {}, [a]), a)
    except ImportError, e:
        raise ImproperlyConfigured, 'ImportError %s: %s' % (app, e.args[0])

    app_dirs.append(os.path.dirname(mod.__file__))

from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.template.context import Context
from genshi.template import MarkupTemplate, TemplateLoader
from genshi.template.loader import TemplateNotFound


'''
configuration:
    GENSHI_TEMPLATE_DIRS:
        specify directories in which to find the genshi template files.
        default value is ('genshi_templates',)
'''

templates_dir_name = 'templates' # 'genshi_templates'

app_template_dirs = []
for app_dir in app_dirs:
    template_dir = os.path.join(app_dir, templates_dir_name)
    if os.path.isdir(template_dir):
        app_template_dirs.append(template_dir)

template_dirs = getattr(settings, 'GENSHI_TEMPLATE_DIRS', None) or (templates_dir_name,)
template_dirs += tuple(app_template_dirs)

loader = TemplateLoader(template_dirs, auto_reload=settings.DEBUG)

def select_template(template_name_list):
    for template_name in template_name_list:
        try:
            return loader.load(template_name)
        except TemplateNotFound:
            pass

    raise TemplateDoesNotExist, 'genshi templates: '+', '.join(template_name_list)

def get_template(template_name):
    try:
        return loader.load(template_name)
    except TemplateNotFound:
        raise TemplateDoesNotExist, 'genshi templates: '+template_name

def render_to_response(template_name, dictionary=None,
        context_instance=None):
    if isinstance(template_name, (list, tuple)):
        template = select_template(template_name)
    else:
        template = get_template(template_name)

    dictionary = dictionary or {}
    if context_instance is None:
        context_instance = Context(dictionary)
    else:
        context_instance.update(dictionary)
    data = {}
    [data.update(d) for d in context_instance]
    stream = template.generate(**data)
    return HttpResponse(stream.render('xhtml'))

def render(template_name, **kwargs):
    return render_to_response(template_name, kwargs)
