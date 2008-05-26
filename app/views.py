# -*- encoding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from genshi.template import TemplateLoader
from genshi.core import Markup
from brewjournal import util
from brewjournal.app import models, widgets
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

def auth_user_is_user(request, user):
    return (request.user.is_authenticated() and request.user == user)

_std_ctx = None
def standard_context():
    global _std_ctx
    if not _std_ctx:
        _std_ctx = {'fmt': { 'date': { 'ymdhm': lambda x: safe_datetime_fmt(x, '%Y-%m-%d %H:%M'),
                                       'ymd': lambda x: safe_datetime_fmt(x, '%Y-%m-%d') } },
                    'markup': Markup,
                    'Markup': Markup,
                    'auth_user_is_user': auth_user_is_user,
                    }
    return _std_ctx

class AuthForm (forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput)

def root_post(request):
    auth_form = AuthForm(request.POST)
    username = request.POST['username']
    password = request.POST['password']
    submit_type = request.POST['sub']
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
    starred_recipes = models.StarredRecipe.objects.filter(user=uri_user)
    return HttpResponse(render('user/index.html', request=request, user=uri_user, std=standard_context(),
                               brews=brews,
                               done_brews=done_brews,
                               starred_recipes=starred_recipes))

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

class BrewForm (forms.ModelForm):
    class Meta:
        model = models.Brew
        exclude = ['brewer']

# sys.stdout = codecs.getwriter('utf-8')(sys.stdout, errors='replace')
def new_brew(request, user_name):
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    form = BrewForm()
    if request.method == 'POST':
        if not (request.user.is_authenticated() and request.user == uri_user):
            return HttpResponseForbidden('not allowed')
        form = BrewForm(request.POST)
        if form.is_valid():
            brew = form.save(commit=False)
            brew.brewer = uri_user
            brew.save()
            return HttpResponseRedirect('/user/%s/brew/%s' % (uri_user.username, brew.id))
    elif request.method == 'GET' and request.GET.has_key('recipe'):
        recipe_id = request.GET['recipe']
        recipe = models.Recipe.objects.get(pk=int(recipe_id))
        brew = models.Brew()
        brew.recipe = recipe
        form = BrewForm(instance=brew)
    return HttpResponse(render('user/brew/new.html', request=request, user=uri_user, brew_form=form, Markup=Markup))

def brew_edit(request,user_name, brew_id):
    '''POST /user/jsled/brew/2 edits'''
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    brew = models.Brew.objects.get(id=brew_id)
    if not brew: return HttpResponseNotFound('no such brew with id [%d]' % (brew_id))
    if request.method == 'POST':
        if not (request.user.is_authenticated() and request.user == uri_user):
            return HttpResponseForbidden()
        form = BrewForm(request.POST, instance=brew)
        if not form.errors:
            updated_brew = form.save(commit=False)
            updated_brew.id = brew.id
            updated_brew.brewer = brew.brewer
            updated_brew.save()
        else:
            # @fixme handle errors...
            pass
    return HttpResponseRedirect('/user/%s/brew/%d/' % (user_name, updated_brew.id))


class StepForm (forms.ModelForm):
    notes = forms.CharField(widget=forms.Textarea(), required=False)
    brew = forms.IntegerField(widget=forms.HiddenInput)
    class Meta:
        model = models.Step
        exclude = ['gravity']


def brew(request, user_name, brew_id, step_id):
    '''
    e.g., /user/jsled/brew/2[/step/3]
    
    @todo when editing an existing step, the type (at least) should not be changeable.
    @fixme method is too big; reduce
    '''
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    brew = models.Brew.objects.get(id=brew_id)
    if not brew: return HttpResponseNotFound('no such brew with id [%d]' % (brew_id))
    brew_form = BrewForm(instance=brew)
    form = None
    step = None
    submit_label = 'Add Step'
    steps_changed = False
    if step_id:
        step = models.Step.objects.get(pk=step_id)
        form = StepForm(instance=step)
        submit_label = 'Update Step'
    if request.method == 'POST':
        if not (request.user.is_authenticated() and request.user == uri_user):
            return HttpResponseForbidden()
        form = StepForm(request.POST, instance=step)
        if form.is_valid():
            step = form.save(commit=False)
            step.brew = brew
            if step.gravity_orig:
                temp = step.gravity_orig_temp or step.temp
                if step.gravity_orig_temp_units == 'c':
                    temp = util.celsius_to_farenheit(temp)
                step.gravity = util.correct_gravity(step.gravity_orig, temp)
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
            next_step_type = models.get_likely_next_step_type_id(last_step_type)
            last_date = last_step.date
            if (datetime.now() - last_step.date).days > 2:
                default_date = last_step.date
        form = StepForm(initial={'brew': brew.id, 'date': default_date, 'type': next_step_type})
    return HttpResponse(render('user/brew/index.html', request=request, std=standard_context(), user=uri_user,
                               brew=brew, steps=steps, step_form=form, submit_label=submit_label,
                               brew_form=brew_form))


style_choices = None

def get_style_choices():
    global style_choices
    if not style_choices:
        style_choices = [('%s (%s)' % (s.name, s.bjcp_code), [(s.id, '%s, uncategorized' % (s.name))]) for s in models.Style.objects.filter(parent__isnull=True)]
        for name,subs in style_choices:
            for sub_style in models.Style.objects.filter(parent = subs[0][0]):
                subs.append( (sub_style.id, '%s (%s)' % (sub_style.name, sub_style.bjcp_code)) )
    return style_choices

grain_choices = None
def get_grain_choices():
    global grain_choices
    if not grain_choices:
        by_group = {}
        for grain in models.Grain.objects.all():
            by_group.setdefault(grain.group, []).append(grain)
        group_names = by_group.keys()
        group_names.sort()
        grain_choices = [(group, [(grain.id, grain.name) for grain in by_group[group]]) for group in group_names]
    return grain_choices

yeast_choices = None
def get_yeast_choices():
    global yeast_choices
    if not yeast_choices:
        by_type = {}
        for yeast in models.Yeast.objects.all():
            by_type.setdefault(yeast.type, []).append(yeast)
            type_names = by_type.keys()
            type_names.sort()
            yeast_choices = [(type, [(yeast.id, str(yeast)) for yeast in by_type[type]]) for type in type_names]
    return yeast_choices


class RecipeForm (forms.ModelForm):
    style = forms.ModelChoiceField(models.Style.objects.all(),
                                   widget=widgets.TwoLevelSelectWidget(choices=get_style_choices()))

    #def __init__(self, *args, **kwargs):
    #    super(RecipeForm, self).__init__(*args, **kwargs)
    #    self.style.choices = style_choices

    class Meta:
        model = models.Recipe
        exclude = ['author', 'source', 'private']

class RecipeGrainForm (forms.ModelForm):
    grain = forms.ModelChoiceField(models.Grain.objects.all(),
                                   widget=widgets.TwoLevelSelectWidget(choices=get_grain_choices()))
    class Meta:
        model = models.RecipeGrain
        exclude = ['recipe']

class RecipeHopForm (forms.ModelForm):
    class Meta:
        model = models.RecipeHop
        exclude = ['recipe']

class RecipeAdjunctForm (forms.ModelForm):
    class Meta:
        model = models.RecipeAdjunct
        exclude = ['recipe']

class RecipeYeastForm (forms.ModelForm):
    yeast = forms.ModelChoiceField(models.Yeast.objects.all(),
                                   widget=widgets.TwoLevelSelectWidget(choices=get_yeast_choices()))
    class Meta:
        model = models.RecipeYeast
        exclude = ['recipe']

def recipe_grain(request, recipe_id):
    return recipe_component_generic(request, recipe_id, models.RecipeGrain, RecipeGrainForm)

def recipe_hop(request, recipe_id):
    return recipe_component_generic(request, recipe_id, models.RecipeHop, RecipeHopForm)

def recipe_adjunct(request, recipe_id):
    return recipe_component_generic(request, recipe_id, models.RecipeAdjunct, RecipeAdjunctForm)

def recipe_yeast(request, recipe_id):
    return recipe_component_generic(request, recipe_id, models.RecipeYeast, RecipeYeastForm)

def recipe_component_generic(request, recipe_id, model_type, form_class):
    '''
    All the additions are going to be the same, so genericize them, leveraging the form to do the heavy lifting.
    '''
    def _get_recipe_redirect(recipe_id):
        return HttpResponseRedirect('/recipe/%s/' % (recipe_id))
    if not request.method == 'POST':
        return HttpResponseBadRequest('method not supported')
    if request.POST.has_key('delete_id') and request.POST['delete_id'] != '-1':
        model_type.objects.get(pk=request.POST['delete_id']).delete()
        return _get_recipe_redirect(recipe_id)
    recipe = models.Recipe.objects.get(pk=recipe_id)
    if not recipe: return HttpResponseNotFound('no such recipe')
    form = form_class(request.POST)
    new_component = form.save(commit=False)
    new_component.recipe = recipe
    new_component.save()
    return _get_recipe_redirect(recipe_id)

def recipe_post(request, recipe_id, recipe=None):
    if not recipe and recipe_id:
        recipe = models.Recipe.objects.get(pk=recipe_id)
    form = RecipeForm(request.POST, instance=recipe)
    upd_recipe = form.save(commit=False)
    if not recipe and request.user.is_authenticated():
        upd_recipe.author = request.user
    else:
        upd_recipe.author = recipe.author
    upd_recipe.save()
    return HttpResponseRedirect('/recipe/%d' % (upd_recipe.id))

def user_recipe_index(request, user_name):
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    if request.method == 'POST':
        rtn = recipe_post(request, None, None)
        if rtn: return rtn
    # populate data for page
    authored = models.Recipe.objects.filter(author=uri_user).order_by('-insert_date')[0:10]
    starred = models.StarredRecipe.objects.filter(user=uri_user).order_by('-when')
    return HttpResponse(render('user/recipe/index.html', request=request, uri_user=uri_user, std=standard_context(),
                               authored_recipes=authored, starred_recipes=starred))

def recipe_new(request):
    # uri_user = User.objects.get(username__exact = user_name)
    # if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    if request.method == 'GET' and request.GET.has_key('clone_from_recipe_id'):
        to_clone = models.Recipe.objects.get(pk=int(request.GET['clone_from_recipe_id']))
        to_clone.name = 'Copy of %s' % (to_clone.name)
        if request.user.is_authenticated():
            to_clone.author = request.user
        to_clone.derived_from_recipe_id = to_clone.id
        cloned_recipe_id = to_clone.id
        to_clone.id = None
        to_clone.save()
        for type in [models.RecipeGrain, models.RecipeHop, models.RecipeAdjunct, models.RecipeYeast]:
            for component in type.objects.filter(recipe=cloned_recipe_id):
                component.recipe = to_clone
                component.id = None
                component.save()
        return HttpResponseRedirect('/recipe/%d/' % (to_clone.id))
    return HttpResponse(render('recipe/new.html', request=request, std=standard_context(),
                               recipe_form=RecipeForm(), is_new=True))

def recipe(request, recipe_id):
    # uri_user = User.objects.get(username__exact = user_name)
    # if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    if request.method == 'POST':
        rtn = recipe_post(request, recipe_id, None)
        if rtn: return rtn
    recipe = models.Recipe.objects.get(pk=recipe_id)
    grains = models.RecipeGrain.objects.filter(recipe=recipe)[0:100]
    hops = models.RecipeHop.objects.filter(recipe=recipe)[0:100]
    adjuncts = models.RecipeAdjunct.objects.filter(recipe=recipe)[0:100]
    yeasts = models.RecipeYeast.objects.filter(recipe=recipe)[0:100]
    return HttpResponse(render('recipe/view.html', request=request, std=standard_context(),
                               recipe=recipe, grains=grains, hops=hops, adjuncts=adjuncts, yeasts=yeasts,
                               recipe_form=RecipeForm(instance=recipe),
                               grain_form=RecipeGrainForm(),
                               hop_form=RecipeHopForm(),
                               adj_form=RecipeAdjunctForm(),
                               yeast_form=RecipeYeastForm()
                               ))
    
