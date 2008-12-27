# -*- encoding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django import forms
from genshi.template import TemplateLoader
from genshi.core import Markup
from brewjournal import util
from brewjournal.app import models, widgets
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

def custom_404(request):
    return HttpResponse(render('404.html', request=request, ctx=standard_context()))

def custom_500(request):
    return HttpResponse(render('500.html', request=request, ctx=standard_context()))

class RegisterForm (forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput)
    password_again = forms.CharField(widget=forms.PasswordInput, required=False)
    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        self._is_reg = kwargs.get('is_reg', False)
        if kwargs.has_key('is_reg'):
            del kwargs['is_reg']
        forms.Form.__init__(self, *args, **kwargs)
    
    def clean(self):
        if self._is_reg:
            data = self.cleaned_data
            if not data.has_key('password') and not data.has_key('password_again'):
                raise forms.ValidationError(u'Matching passwords required')
            if data['password'] != data['password_again']:
                raise forms.ValidationError(u'Passwords must match')
            #if not data.has_key('email') or data['email'] == u'':
            #    raise forms.ValidationError('Must have valid email')
        return self.cleaned_data
            

def root_post(request):
    username = request.POST['username']
    password = request.POST['password']
    submit_type = request.POST['sub']
    auth_form = RegisterForm(request.POST, is_reg=submit_type == 'create')
    auth_errors = forms.util.ErrorList()
    if submit_type == 'create':
        user = None
        try:
            user = User.objects.get(username__exact = username)
        except User.DoesNotExist:
            pass
        if user:
            auth_errors = forms.util.ErrorList([u'Username [%s] is unavailable' % (username)])
        else:
            if not auth_form.is_valid():
                return root_common(request, auth_form)
            email = request.POST['email']
            user = User.objects.create_user(auth_form.cleaned_data['username'],
                                            auth_form.cleaned_data['email'],
                                            auth_form.cleaned_data['password'])
            if not user:
                auth_errors = forms.util.ErrorList([u'unknown error creating user [%s]' % (username)])
            user = authenticate(username = auth_form.cleaned_data['username'],
                                password = auth_form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/user/%s/profile' % (username))
        pass
    elif submit_type == 'login':
        user = authenticate(username = username,
                            password = password)
        if not user:
            auth_errors = forms.util.ErrorList([u'invalid username or password'])
            pass
        elif not user.is_active:
            auth_errors = forms.util.ErrorList([u'account has been disabled'])
            pass
        else:
            login(request, user)
            return HttpResponseRedirect('/user/%s/' % (user.username))
    else:
        auth_errors = forms.util.ErrorList([u'unknown form submission style [%s]' % (submit_type)])
        pass
    return root_common(request, auth_form, auth_errors)

def root_common(request, auth_form = None, auth_errors = forms.util.ErrorList()):
    recent_brews = models.Brew.objects.order_by('-brew_date')[0:10]
    recent_recipes = models.Recipe.objects.order_by('-insert_date')[0:10]
    recent_updates = models.Step.objects.order_by('-date')[0:10]
    return HttpResponse(render('index.html', request=request, std=standard_context(), auth_form=auth_form,
                               auth_errors=auth_errors,
                               recent_brews=recent_brews,
                               recent_recipes=recent_recipes,
                               recent_updates=recent_updates))
    

def root(request):
    if request.method == 'POST':
        rtn = root_post(request)
        if rtn:
            return rtn
    return root_common(request, RegisterForm())


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def user_index(request, user_name):
    try:
        uri_user = User.objects.get(username__exact = user_name)
    except User.DoesNotExist:
        raise Http404
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


def user_shopping_list(request, user_name):
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    pre_brews = models.Brew.objects.brews_pre_brew(uri_user)
    shopping_list = models.ShoppingList(pre_brews)
    return HttpResponse(render('user/shopping-list.html', request=request, user=uri_user, std=standard_context(),
                               shopping_list = shopping_list))
                               

def brew_edit(request, user_name, brew_id):
    '''
    POST /user/jsled/brew/2/edit
    @fixme this is lame.  Make GET an error, use form.is_valid(), integrate with brew(…).
    '''
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


def brew_post(request, uri_user, brew, step):
    if not (request.user.is_authenticated() and request.user == uri_user):
        return HttpResponseForbidden()
    step_form = StepForm(request.POST, instance=step)
    if step_form.is_valid():
        step_form.cleaned_data['brew'] = brew
        step = step_form.save()
        try:
            steps = models.Step.objects.filter(brew__id = brew.id)
        except models.Step.DoesNotExist:
            pass
        brew.update_from_steps(steps)
        brew.save()
        return HttpResponseRedirect('/user/%s/brew/%d/' % (brew.brewer.username, brew.id))
    return brew_render(request, uri_user, brew, step_form, True)


def brew_render(request, uri_user, brew, step_form, step_edit):
    steps = [step for step in brew.step_set.all()]
    brew_form = BrewForm(instance=brew)
    return HttpResponse(render('user/brew/index.html', request=request, std=standard_context(), user=uri_user,
                               brew=brew, steps=steps, step_form=step_form, step_edit=step_edit,
                               brew_form=brew_form, deriv=util.BrewDerivations(brew)))
    

def brew(request, user_name, brew_id, step_id):
    '''
    e.g., /user/jsled/brew/2/[step/3], /user/jsled/brew/2/?type=pitch
    '''
    uri_user = User.objects.get(username__exact = user_name)
    if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    brew = models.Brew.objects.get(id=brew_id)
    if not brew: return HttpResponseNotFound('no such brew with id [%d]' % (brew_id))
    step = None
    if step_id:
        step = models.Step.objects.get(pk=step_id)
        if not step: return HttpResponseNotFound('no such user [%s] brew [%s] step id [%s]' % (user_name, brew_id, step_id))
    if request.method == 'POST':
        return brew_post(request, uri_user, brew, step)
    # else:
    step_form = None
    step_edit = False
    if step:
        step_form = StepForm(instance=step)
        step_edit = True
    if not step_form:
        default_date = datetime.now()
        explicit_type = request.method == 'GET' and request.GET.has_key('type')
        next_step_type = 'starter'
        if explicit_type:
            next_step_type = request.GET['type']
            step_edit = True
        else:
            step_edit, step_form = _lame_compute_next_steps(brew, default_date)
        if not step_form:
            step_form = StepForm(initial={'brew': brew.id, 'date': default_date, 'type': next_step_type})
    return brew_render(request, uri_user, brew, step_form, step_edit)

def _lame_compute_next_steps(brew, default_date):
    step_edit = False
    form = None
    steps = [step for step in brew.step_set.all()]
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
    return step_edit, form


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


def _group_items(item_gen_fn, item_grouping_key_accessor_fn, item_label_gen_fn):
    by_group = {}
    for item in item_gen_fn():
        by_group.setdefault(item_grouping_key_accessor_fn(item), []).append(item)
    group_keys = by_group.keys()
    group_keys.sort()
    item_choices = [(group, [(item.id, item_label_gen_fn(item)) for item in by_group[group]]) for group in group_keys]
    return item_choices
    

grain_choices = None
def get_grain_choices():
    global grain_choices
    if not grain_choices:
        def _get_grains(): return models.Grain.objects.all()
        def _get_grouping_key(grain): return grain.group
        def _get_label(grain): return grain.name
        grain_choices = _group_items(_get_grains, _get_grouping_key, _get_label)
    return grain_choices


yeast_choices = None
def get_yeast_choices():
    global yeast_choices
    if not yeast_choices:
        def _get_yeasts() : return models.Yeast.objects.all()
        def _get_grouping_key(yeast): return yeast.type
        def _get_label(yeast): return str(yeast)
        yeast_choices = _group_items(_get_yeasts, _get_grouping_key, _get_label)
    return yeast_choices


adjunct_choices = None
def get_adjunct_choices():
    global adjunct_choices
    if not adjunct_choices:
        def _get_adjuncts(): return models.Adjunct.objects.all()
        def _get_grouping_key(adj): return adj.group
        def _get_label(adj): return adj.name
        adjunct_choices = _group_items(_get_adjuncts, _get_grouping_key, _get_label)
    return adjunct_choices


class RecipeForm (forms.ModelForm):
    style = forms.ModelChoiceField(models.Style.objects.all(),
                                   widget=widgets.TwoLevelSelectWidget(choices=get_style_choices()))
    name = forms.CharField(widget=forms.TextInput(attrs={'size': 40}))
    source_url = forms.URLField(required=False, widget=forms.TextInput(attrs={'size': 40}))
    
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
    adjunct = forms.ModelChoiceField(models.Adjunct.objects.all(),
                                     widget=widgets.TwoLevelSelectWidget(choices=get_adjunct_choices()))
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
    return recipe_component_generic(request, recipe_id, models.RecipeGrain, 'grain_form', RecipeGrainForm)

def recipe_hop(request, recipe_id):
    return recipe_component_generic(request, recipe_id, models.RecipeHop, 'hop_form', RecipeHopForm)

def recipe_adjunct(request, recipe_id):
    return recipe_component_generic(request, recipe_id, models.RecipeAdjunct, 'adj_form', RecipeAdjunctForm)

def recipe_yeast(request, recipe_id):
    return recipe_component_generic(request, recipe_id, models.RecipeYeast, 'yeast_form', RecipeYeastForm)

def recipe_component_generic(request, recipe_id, model_type, type_form_name, form_class):
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
    if not form.is_valid():
        return _render_recipe(request, recipe, **{type_form_name: form})
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


def _render_recipe(request, recipe, **kwargs):
    form = kwargs.setdefault('form', RecipeForm(instance=recipe))
    grains = models.RecipeGrain.objects.filter(recipe=recipe)
    hops = models.RecipeHop.objects.filter(recipe=recipe)
    adjuncts = models.RecipeAdjunct.objects.filter(recipe=recipe)
    yeasts = models.RecipeYeast.objects.filter(recipe=recipe)
    grain_form = kwargs.setdefault('grain_form', RecipeGrainForm())
    hop_form = kwargs.setdefault('hop_form', RecipeHopForm())
    adj_form = kwargs.setdefault('adj_form', RecipeAdjunctForm())
    yeast_form = kwargs.setdefault('yeast_form', RecipeYeastForm())
    return HttpResponse(render('recipe/view.html', request=request, std=standard_context(),
                               recipe=recipe, grains=grains, hops=hops, adjuncts=adjuncts, yeasts=yeasts,
                               recipe_form=form,
                               grain_form=grain_form,
                               hop_form=hop_form,
                               adj_form=adj_form,
                               yeast_form=yeast_form
                               ))

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
    return _render_recipe(request, recipe)
