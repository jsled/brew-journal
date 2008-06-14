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
import urllib

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
    recent_brews = models.Brew.objects.order_by('-brew_date')[0:10]
    recent_recipes = models.Recipe.objects.order_by('-insert_date')[0:10]
    recent_updates = models.Step.objects.order_by('-date')[0:10]
    auth_form = AuthForm()
    return HttpResponse(render('index.html', request=request, std=standard_context(), auth_form=auth_form,
                               recent_brews=recent_brews,
                               recent_recipes=recent_recipes,
                               recent_updates=recent_updates))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def user_index(request, user_name):
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    brews = models.Brew.objects.filter(brewer=uri_user, is_done=False)
    future_brews = models.Brew.objects.brews_with_future_steps(uri_user)
    future_steps = models.Step.objects.future_steps_for_user(uri_user).order_by('date')
    done_brews = models.Brew.objects.filter(brewer=uri_user, is_done=True)
    starred_recipes = models.StarredRecipe.objects.filter(user=uri_user)
    authored_recipes = models.Recipe.objects.filter(author=uri_user).order_by('-insert_date')[0:10]
    return HttpResponse(render('user/index.html', request=request, user=uri_user, std=standard_context(),
                               brews=brews,
                               future_brews=future_brews,
                               future_steps=future_steps,
                               done_brews=done_brews,
                               authored_recipes=authored_recipes,
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
        exclude = ['brewer', 'recipe']

# sys.stdout = codecs.getwriter('utf-8')(sys.stdout, errors='replace')
def user_brew_new(request, user_name):
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    recipe = None
    form = BrewForm()
    if request.method == 'POST':
        if not (request.user.is_authenticated() and request.user == uri_user):
            return HttpResponseForbidden('not allowed')
        form = BrewForm(request.POST)
        if form.is_valid():
            brew = form.save(commit=False)
            if not request.POST.has_key('recipe_id'):
                name = 'unknown'
                if request.POST.has_key('brew_name'):
                    name = request.POST['brew_name']
                anon_recipe = models.Recipe.objects.create(author=uri_user,
                                                           name=name,
                                                           batch_size=0)
                brew.recipe = anon_recipe
            else:
                recipe_id = int(request.POST['recipe_id'])
                brew.recipe = models.Recipe.objects.get(pk=recipe_id)
            brew.brewer = uri_user
            brew.save()
            return HttpResponseRedirect('/user/%s/brew/%s' % (uri_user.username, brew.id))
    elif request.method == 'GET' and request.GET.has_key('recipe_id'):
        recipe_id = request.GET['recipe_id']
        recipe = models.Recipe.objects.get(pk=int(recipe_id))
        brew = models.Brew()
        brew.recipe = recipe
        form = BrewForm(instance=brew)
    return HttpResponse(render('user/brew/new.html', request=request, user=uri_user, std=standard_context(),
                               recipe=recipe, brew_form=form))

def brew_edit(request, user_name, brew_id):
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
    step_edit = False
    submit_label = 'add step'
    steps_changed = False
    if step_id:
        step = models.Step.objects.get(pk=step_id)
        form = StepForm(instance=step)
        submit_label = 'update step'
        step_edit = True
    if request.method == 'POST':
        if not (request.user.is_authenticated() and request.user == uri_user):
            return HttpResponseForbidden()
        form = StepForm(request.POST, instance=step)
        if form.is_valid():
            step = form.save(commit=False)
            step.brew = brew
            step.save()
            steps_changed = True
        else:
            step_edit = True
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
        explicit_type = request.method == 'GET' and request.GET.has_key('type')
        next_step_type = 'starter'
        if explicit_type:
            next_step_type = request.GET['type']
            step_edit = True
        else:
            if len(steps) > 0:
                non_future_steps = [step for step in steps if not step.in_future()]
                if len(non_future_steps) > 0:
                    last_step = non_future_steps[-1]
                    if (datetime.now() - last_step.date).days > 2:
                        default_date = last_step.date
                next_step_types = brew.next_step_types()
                if len(next_step_types) > 0:
                    id,step = next_step_types[0]
                    if not id:
                        next_step_type = step.id
                    else:
                        step_edit = True
                        form = StepForm(initial={'date': default_date}, instance=step)
        if not form:
            form = StepForm(initial={'brew': brew.id, 'date': default_date, 'type': next_step_type})
    return HttpResponse(render('user/brew/index.html', request=request, std=standard_context(), user=uri_user,
                               brew=brew, steps=steps, step_form=form, step_edit=step_edit, submit_label=submit_label,
                               brew_form=brew_form, deriv=util.BrewDerivations(brew)))


class StarForm (forms.ModelForm):
    class Meta:
        model = models.StarredRecipe
        exclude = ['recipe', 'user', 'when']


def user_star(request, user_name):
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    if request.method == 'GET':
        if request.GET.has_key('recipe_id'):
            recipe_id = int(request.GET['recipe_id'])
            recipe = models.Recipe.objects.get(pk=recipe_id)
            return HttpResponse(render('user/star.html', request=request, std=standard_context(), user=uri_user,
                                       form=StarForm(), recipe=recipe))
    elif request.method == 'POST':
        if request.POST.has_key('recipe_id'):
            recipe_id = int(request.GET['recipe_id'])
            recipe = models.Recipe.objects.get(pk=recipe_id)
            form = StarForm(request.POST)
            star = form.save(commit=False)
            star.recipe = recipe
            star.user = uri_user
            star.save()
            return HttpResponseRedirect('/user/%s/' % (user_name))
    return HttpResponseBadRequest('bad request')


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
    name = forms.CharField(widget=forms.TextInput(attrs={'size': 40}))
    source_url = forms.URLField(widget=forms.TextInput(attrs={'size': 40}))
    
    class Meta:
        model = models.Recipe
        exclude = ['author', 'derived_from_recipe']


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
        return HttpResponseRedirect('/recipe/%s' % (recipe_id))
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

def recipe_new(request):
    # uri_user = User.objects.get(username__exact = user_name)
    # if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    recipe = None
    recipe_form = RecipeForm()
    clone_id = None
    if request.method == 'GET' and request.GET.has_key('clone_from_recipe_id'):
        clone_id = request.GET['clone_from_recipe_id']
        to_clone = models.Recipe.objects.get(pk=int(clone_id))
        recipe_form = RecipeForm(instance=to_clone,
                                 initial={'name': 'Clone of %s' % (to_clone.name),
                                          'derived_from_recipe': to_clone})
    elif request.method == 'POST':
        clone_id = None
        if request.POST.has_key('clone_from_recipe_id') \
           and len(request.POST['clone_from_recipe_id']) > 0:
            clone_id = int(request.POST['clone_from_recipe_id'])
        form = RecipeForm(request.POST)
        if clone_id:
            to_clone = models.Recipe.objects.get(pk=int(clone_id))
            form = RecipeForm(request.POST, instance=to_clone)
        if not form.is_valid():
            return HttpResponse(render('recipe/new.html', request=request, std=standard_context(),
                                       clone_from_recipe_id=clone_id,
                                       recipe_form=form,
                                       is_new=True))

        new_recipe = form.save(commit=False)
        if request.user.is_authenticated():
            new_recipe.author = request.user
        if clone_id:
            to_clone = models.Recipe.objects.get(pk=clone_id)
            new_recipe.derived_from_recipe = to_clone
        new_recipe.id = None
        new_recipe.save()
        if clone_id:
            to_clone = models.Recipe.objects.get(pk=clone_id)
            for type in [models.RecipeGrain, models.RecipeHop, models.RecipeAdjunct, models.RecipeYeast]:
                for component in type.objects.filter(recipe=to_clone):
                    component.recipe = new_recipe
                    component.id = None
                    component.save()
        return HttpResponseRedirect('/recipe/%d/%s' % (new_recipe.id, urllib.quote(new_recipe.name.encode('utf-8'))))
    return HttpResponse(render('recipe/new.html', request=request, std=standard_context(),
                               clone_from_recipe_id=clone_id,
                               recipe_form=recipe_form,
                               is_new=True))


def recipe_post(request, recipe_id, recipe=None):
    '''@return (successOrError:boolean, formOrHttpResposne)'''
    if not recipe and recipe_id:
        recipe = models.Recipe.objects.get(pk=recipe_id)
    form = RecipeForm(request.POST, instance=recipe)
    if not form.is_valid():
        return (False, form)
    upd_recipe = form.save(commit=False)
    if not recipe and request.user.is_authenticated():
        upd_recipe.author = request.user
    else:
        upd_recipe.author = recipe.author
    upd_recipe.save()
    return (True, HttpResponseRedirect('/recipe/%d/%s' % (upd_recipe.id, urllib.quote(upd_recipe.name.encode('utf-8')))))


def recipe(request, recipe_id, recipe_name):
    # uri_user = User.objects.get(username__exact = user_name)
    # if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    form = None
    if request.method == 'POST':
        success,thing = recipe_post(request, recipe_id, None)
        if success:
            return thing
        else:
            form = thing
    recipe = models.Recipe.objects.get(pk=recipe_id)
    if not form:
        form = RecipeForm(instance=recipe)
    grains = models.RecipeGrain.objects.filter(recipe=recipe)[0:100]
    hops = models.RecipeHop.objects.filter(recipe=recipe)[0:100]
    adjuncts = models.RecipeAdjunct.objects.filter(recipe=recipe)[0:100]
    yeasts = models.RecipeYeast.objects.filter(recipe=recipe)[0:100]
    return HttpResponse(render('recipe/view.html', request=request, std=standard_context(),
                               recipe=recipe, grains=grains, hops=hops, adjuncts=adjuncts, yeasts=yeasts,
                               recipe_form=form,
                               grain_form=RecipeGrainForm(),
                               hop_form=RecipeHopForm(),
                               adj_form=RecipeAdjunctForm(),
                               yeast_form=RecipeYeastForm()
                               ))

