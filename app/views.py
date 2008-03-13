# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from genshi.template import TemplateLoader
from genshi.core import Markup
from brewlog import util
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

def safe_datetime_fmt(dt, fmt):
    if not dt:
        return ''
    return dt.strftime(fmt)

_std_ctx = None
def standard_context():
    global _std_ctx
    if not _std_ctx:
        _std_ctx = {'fmt': { 'date': { 'ymdhm': lambda x: safe_datetime_fmt(x, '%Y-%m-%d %H:%M'),
                                       'ymd': lambda x: safe_datetime_fmt(x, '%Y-%m-%d') } },
                    'markup': Markup,
                    'Markup': Markup,
                    }
    return _std_ctx

class AuthForm (forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput)

def root_post(request):
    auth_form = AuthForm(request.POST)
    username = request.POST['username']
    password = request.POST['password']
    submit_type = request.POST['submit']
    if submit_type == 'create':
        user = None
        try:
            user = User.objects.get(username__exact = username)
        except User.DoesNotExist:
            pass
        if user:
            # error; user already existss
            return HttpResponseBadRequest('user with username [%s] already exists' % (username))
        else:
            user = User.objects.create_user(username, '', password)
            if not user:
                # error creating user
                return HttpResponseServerError('unknown error creating user [%s]' % (username))
            user = authenticate(username = username, password = password)
            login(request, user)
            return HttpResponseRedirect('/user/%s/profile' % (username))
        pass
    elif submit_type == 'login':
        user = authenticate(username = username,
                            password = password)
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

def root(request):
    if request.method == 'POST':
        rtn = root_post(request)
        if rtn:
            return rtn
    recent_updates = models.Step.objects.order_by('-date')[0:10]
    auth_form = AuthForm()
    return HttpResponse(render('index.html', request=request, std=standard_context(), auth_form=auth_form, recent_updates=recent_updates))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def user_index(request, user_name):
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    brews = models.Brew.objects.filter(brewer=uri_user, is_done=False)
    done_brews = models.Brew.objects.filter(brewer=uri_user, is_done=True)
    return HttpResponse(render('user/index.html', request=request, user=uri_user, brews=brews, done_brews=done_brews, std=standard_context()))

class UserProfileForm (forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','email')
    new_pass_1 = forms.CharField(widget=forms.PasswordInput, label="change password", required=False)
    new_pass_2 = forms.CharField(widget=forms.PasswordInput, label="change password (again)", required=False)

def user_profile(request, user_name):
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    if request.user.is_authenticated() and request.user != uri_user:
        return HttpResponseForbidden('you [%s] can access the profile for user [%s]' % (request.user.username, uri_user.userrname))
    profile_form = UserProfileForm(instance=uri_user)
    if request.method == 'POST':
        # handle save
        profile_form = UserProfileForm(request.POST, instance=uri_user)
        if not profile_form.errors:
            new_user = profile_form.save(commit=False)
            uri_user.first_name = new_user.first_name
            uri_user.last_name = new_user.last_name
            uri_user.email = new_user.email
            new_pass_1,new_pass_2 = request.POST['new_pass_1'],request.POST['new_pass_2']
            if new_pass_1 and new_pass_1 == new_pass_2:
                uri_user.set_password(new_pass_1)
            uri_user.save()
            return HttpResponseRedirect('/user/%s' % (uri_user.username))
    return HttpResponse(render('user/profile.html', request=request, user=uri_user, profile_form=profile_form, std=standard_context()))

# sys.stdout = codecs.getwriter('utf-8')(sys.stdout, errors='replace')
def new_brew(request, user_name):
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    form_gen = forms.form_for_model(models.Brew)
    form = form_gen()
    if request.method == 'POST':
        if not (request.user.is_authenticated() and request.user == uri_user):
            return HttpResponseForbidden('not allowed')
        form = form_gen(request.POST)
        if form.is_valid():
            brew = form.save()
            return HttpResponseRedirect('/user/%s/brew/%s' % (uri_user.username, brew.id))
    return HttpResponse(render('user/brew/new.html', request=request, user=uri_user, brew_form=form, Markup=Markup))

class StepForm (forms.ModelForm):
    notes = forms.CharField(widget=forms.Textarea(), required=False)
    brew = forms.IntegerField(widget=forms.HiddenInput)
    class Meta:
        model = models.Step

def brew(request, user_name, brew_id, step_id):
    '''
    e.g., /user/jsled/brew/2[/step/3]
    
    @todo time should be a function of the last step time, unless it is outside epsilon of `now`.
    @todo when editing an existing step, the type (at least) should not be changeable.
    '''
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    brew = models.Brew.objects.get(id=brew_id)
    if not brew: return HttpResponseNotFound('no such brew with id [%d]' % (brew_id))
    form = None
    step = None
    submit_label = 'Add Step'
    steps_changed = False
    if step_id:
        step = models.Step.objects.get(pk=step_id)
        form = StepForm(instance=step)
        submit_label = 'Update Step'
        print u'step_id [%s] = step [%s]' % (step_id, step)
    if request.method == 'POST':
        if not (request.user.is_authenticated() and request.user == uri_user):
            return HttpResponseForbidden()
        form = StepForm(request.POST, instance=step)
        if form.is_valid():
            step = form.save(commit=False)
            step.brew = brew
            step.save()
            steps_changed = True
    steps = []
    try:
        steps = models.Step.objects.filter(brew__id = brew.id)
    except models.Step.DoesNotExist:
        pass
    if steps_changed:
        brew.update_from_steps(steps)
        brew.save()
        return HttpResponseRedirect('/user/%s/brew/%d/' % (brew.brewer.username, brew.id))
    if not form:
        default_date = datetime.now()
        next_step_type = 'strike'
        if len(steps) > 0:
            last_step = steps[len(steps)-1]
            last_step_type = last_step.type
            next_step_type = models.get_likely_next_step_type(last_step_type)
            last_date = last_step.date
            if (datetime.now() - last_step.date).days > 2:
                default_date = last_step.date
        form = StepForm(initial={'brew': brew.id, 'date': default_date, 'type': next_step_type})
    return HttpResponse(render('user/brew/index.html', request=request, std=standard_context(), user=uri_user, brew=brew, steps=steps, step_form=form, submit_label=submit_label))
