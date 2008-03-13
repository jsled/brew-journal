# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from genshi.template import TemplateLoader
from genshi.core import Markup
from brewlog.app import models
from django import newforms as forms
from datetime import datetime

genshi_template_loader = None
def init_genshi():
    global genshi_template_loader
    genshi_template_loader = TemplateLoader(['./app/tmpl'], auto_reload=True, default_encoding='utf-8')

def render(template_name, **kwargs):
    if not genshi_template_loader:
        init_genshi()
    tmpl = genshi_template_loader.load(template_name)
    stream = tmpl.generate(**kwargs)
    return stream.render()

_std_ctx = None
def standard_context():
    global _std_ctx
    if not _std_ctx:
        _std_ctx = {'fmt': { 'date': lambda x: x.strftime('%x %X') },
                    'markup': Markup,
                    'Markup': Markup,
                    }
    return _std_ctx

class AuthForm (forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput)

def root(request):
    auth_form = AuthForm()
    if request.method == 'POST':
        auth_form = AuthForm(request.POST)
        submit_type = request.POST['submit']
        if submit_type == 'create':
            # @fixme create new user
            pass
        elif submit_type == 'login':
            # auth.
            user = authenticate(username = request.POST['username'],
                                password = request.POST['password'])
            if not user:
                # error: username/password incorrect
                pass
            elif not user.is_active:
                # error: disabled account
                pass
            else:
                login(request, user)
                return HttpResponseRedirect('/user/%s/' % (user.username))
        else:
            # error
            pass
    return HttpResponse(render('index.html', request=request, std=standard_context(), auth_form=auth_form))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
    

def user_index(request, user_name):
    u = User.objects.get(username__exact = user_name)
    if not u: return HttpResponseNotFound('no such user [%s]' % (user_name))
    brews = models.Brew.objects.filter(brewer=u)
    return HttpResponse(render('user/index.html', request=request, user=u, brews=brews))

# sys.stdout = codecs.getwriter('utf-8')(sys.stdout, errors='replace')
def new_brew(request, user_name):
    u = User.objects.get(username__exact = user_name)
    if not u: return HttpResponseNotFound('no such user [%s]' % (user_name))
    form_gen = forms.form_for_model(models.Brew)
    form = form_gen()
    if request.method == 'POST':
        form = form_gen(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/user/%s' % (u.username))
    return HttpResponse(render('user/brew/new.html', request=request, user=u, brew_form=form, Markup=Markup))

class StepForm (forms.ModelForm):
    notes = forms.CharField(widget=forms.Textarea())
    brew = forms.IntegerField(widget=forms.HiddenInput)
    class Meta:
        model = models.Step

def brew(request, user_name, brew_id, step_id):
    '''
    /user/jsled/brew/2[/step/3]
    
    @todo time should be a function of the last step time, unless it is outside epsilon of `now`.
    @todo when editing an existing step, the type (at least) shouldn't be changeable.
    ''' # emacs '
    u = User.objects.get(username__exact = user_name)
    if not u: return HttpResponseNotFound('no such user [%s]' % (user_name))
    brew = models.Brew.objects.get(id=brew_id)
    if not brew: return HttpResponseNotFound('no such brew with id [%d]' % (brew_id))
    form = None
    step = None
    submit_label = 'Add Step'
    if step_id:
        step = models.Step.objects.get(pk=step_id)
        form = StepForm(instance=step)
        submit_label = 'Update Step'
        print u'step_id [%s] = step [%s]' % (step_id, step)
    if request.method == 'POST':
        form = StepForm(request.POST, instance=step)
        if form.is_valid():
            form.save()
        # @fixme: update the brew last_updated and state based on new step data.
    steps = []
    try:
        steps = models.Step.objects.filter(brew__id = brew.id)
    except models.Step.DoesNotExist:
        pass
    if not form:
        next_step_type = 'strike'
        if len(steps) > 0:
            last_step_type = steps[len(steps)-1].type
            next_step_type = models.get_likely_next_step_type(last_step_type)
            print u'got next step [%s]' % (next_step_type)
        form = StepForm(initial={'brew': brew.id, 'date': datetime.now(), 'type': next_step_type})
    return HttpResponse(render('user/brew/index.html', request=request, std=standard_context(), user=u, brew=brew, steps=steps, step_form=form, submit_label=submit_label))
