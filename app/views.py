# -*- encoding: utf-8 -*-

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

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from genshi.core import Markup
from brewjournal.app import models, widgets
from datetime import datetime
import urllib

from timezones.forms import LocalizedDateTimeField
from timezones.utils import adjust_datetime_to_timezone

from genshi_django import render

class LocalizedDateTimeInput (forms.DateTimeInput):
    def __init__(self, tz):
        self._tz = tz
        super(LocalizedDateTimeInput, self).__init__()

    def render(self, name, value, attrs=None):
        if isinstance(value, datetime):
            value = adjust_datetime_to_timezone(value, 'UTC', self._tz)
        # @fixme: output the string rep of the timezone, probably after the <input>
        return super(LocalizedDateTimeInput, self).render(name, value, attrs)

def datetime_span(formatted):
    return Markup('<span class="datetime">%s</span>' % (formatted))

def tz_adjust(date, user):
    settings_tz = settings.TIME_ZONE
    tz = settings_tz
    if user and hasattr(user, 'get_profile'):
        try:
            profile_tz = user.get_profile().timezone
            if profile_tz:
                tz = profile_tz
        except models.UserProfile.DoesNotExist:
            pass
    rtn = adjust_datetime_to_timezone(date, settings_tz, tz)
    # print 'adjusting date %s from %s to %s is %s' % (date, settings_tz, tz, rtn)
    return rtn

def safe_datetime_fmt_raw(dt, fmt, user):
    if not dt:
        return ''
    dt = tz_adjust(dt, user)
    return dt.strftime(fmt)

def safe_datetime_fmt(dt, fmt, user=None):
    return datetime_span(safe_datetime_fmt_raw(dt, fmt, user))
                         
def safe_graceful_datetime_fmt(dt, ymd_fmt, ymdhm_fmt, user=None):
    if not dt:
        return ''
    dt = tz_adjust(dt, user)
    best_fmt = ymdhm_fmt
    if (dt.hour == 0 and dt.minute == 0) or (dt.hour == 23 and dt.minute == 59):
        best_fmt = ymd_fmt
    return datetime_span(dt.strftime(best_fmt))

def auth_user_is_user(request, user):
    return (request.user.is_authenticated() and request.user == user)

_std_ctx = None
def standard_context():
    global _std_ctx
    if not _std_ctx:
        YMDHM_FMT = '%Y-%m-%d %H:%M %Z'
        YMD_FMT = '%Y-%m-%d'
        _std_ctx = {'fmt': { 'date': { 'ymdhm': lambda x,user=None: safe_datetime_fmt(x, YMDHM_FMT, user),
                                       'ymd': lambda x,user=None: safe_datetime_fmt(x, YMD_FMT, user),
                                       'best': lambda x,user=None: safe_graceful_datetime_fmt(x, YMD_FMT, YMDHM_FMT, user),
                                       } },
                    'markup': Markup,
                    'Markup': Markup,
                    'auth_user_is_user': auth_user_is_user,
                    }
    return _std_ctx

def custom_404(request):
    return HttpResponseNotFound(render('404.html', request=request, ctx=standard_context()))

def custom_500(request):
    return HttpResponseServerError(render('500.html', request=request, ctx=standard_context()))

def intentional_500(request):
    raise Exception('intentional 500 to test handling')

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
            if not data.has_key('password') \
               or not data.has_key('password_again') \
               or data['password'] != data['password_again']:
                raise forms.ValidationError(u'Matching passwords required')
            if not data.has_key('email')  or data['email'] == u'':
                raise forms.ValidationError('Must have valid email')
        return self.cleaned_data


def test_maybe_create_user_profile(user):
    try:
        profile = user.get_profile()
    except models.UserProfile.DoesNotExist,e:
        user_profile = models.UserProfile(user=user)
        user_profile.save()
           

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
        except ObjectDoesNotExist:
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
            test_maybe_create_user_profile(user)
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
            test_maybe_create_user_profile(user)
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
    except User.DoesNotExist,e:
        raise Http404
    brews = models.Brew.objects.filter(brewer=uri_user, is_done=False).order_by('-brew_date')
    future_brews = models.Brew.objects.brews_with_future_steps(uri_user)
    future_steps = models.Step.objects.future_steps_for_user(uri_user).order_by('date')
    shopping_list = models.ShoppingList(uri_user)
    done_brews = models.Brew.objects.filter(brewer=uri_user, is_done=True)
    starred_recipes = models.StarredRecipe.objects.filter(user=uri_user)
    authored_recipes = models.Recipe.objects.filter(author=uri_user).order_by('-insert_date')[0:10]
    efficiency_tracker = EfficiencyTracker(uri_user)
    return HttpResponse(render('user/index.html', request=request, user=uri_user, std=standard_context(),
                               brews=brews,
                               future_brews=future_brews,
                               future_steps=future_steps,
                               done_brews=done_brews,
                               shopping_list=shopping_list,
                               authored_recipes=authored_recipes,
                               starred_recipes=starred_recipes,
                               efficiency_tracker=efficiency_tracker))


class UserProfileForm (forms.ModelForm):
    rototill_dates = forms.BooleanField(help_text='If set, when changing your timezone, any existing Recipe and Brew timestamps will be converted to be in that timezone, as you originally intended.', initial=True)
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    new_pass_1 = forms.CharField(widget=forms.PasswordInput, label="change password", required=False)
    new_pass_2 = forms.CharField(widget=forms.PasswordInput, label="change password (again)", required=False)

    class Meta:
        model = models.UserProfile
        exclude = ('user')


def rototill_dates(uri_user, old_tz, new_tz):
    results = {'recipes_updated':0,
               'brews_updated': 0}
    for recipe in models.Recipe.objects.filter(author=uri_user):
        if recipe.insert_date:
            recipe.insert_date = adjust_datetime_to_timezone(recipe.insert_date, new_tz, old_tz)
            recipe.save()
            results['recipes_updated'] += 1
    for brew in models.Brew.objects.filter(brewer=uri_user):
        updated = False
        if brew.brew_date:
            brew.brew_date = adjust_datetime_to_timezone(brew.brew_date, new_tz, old_tz)
            updated = True
        if brew.last_update_date:
            brew.last_update_date = adjust_datetime_to_timezone(brew.last_update_date, new_tz, old_tz)
            updated = True
        if updated:
            brew.save()
            results['brews_updated'] += 1
        for step in brew.step_set.all():
            updated = False
            if step.date:
                step.date = adjust_datetime_to_timezone(step.date, new_tz, old_tz)
                updated = True
            if step.entry_date:
                step.entry_date = adjust_datetime_to_timezone(step.entry_date, new_tz, old_tz)
                updated = True
            if updated:
                step.save()
    return results


def user_profile(request, user_name):
    try:
        uri_user = User.objects.get(username__exact = user_name)
    except User.DoesNotExist:
        raise Http404
    if request.user.is_authenticated() and request.user != uri_user:
        return HttpResponseForbidden('you [%s] can access the profile for user [%s]' % (request.user.username, uri_user.userrname))
    profile_form = UserProfileForm(initial={'first_name': uri_user.first_name,
                                            'last_name': uri_user.last_name,
                                            'email': uri_user.email},
                                   instance=uri_user.get_profile())
    if request.method == 'POST':
        # handle save
        profile_form = UserProfileForm(request.POST, instance=uri_user.get_profile())
        if not profile_form.errors:
            old_tz = uri_user.get_profile().timezone
            profile = profile_form.save(commit=False)
            profile.user = uri_user
            profile.save()
            #
            cleaned_data = profile_form.cleaned_data
            uri_user.first_name = cleaned_data['first_name']
            uri_user.last_name = cleaned_data['last_name']
            uri_user.email = cleaned_data['email']
            # @fixme: move to the form's clean() method.
            new_pass_1,new_pass_2 = cleaned_data['new_pass_1'], cleaned_data['new_pass_2']
            if new_pass_1 and new_pass_1 == new_pass_2:
                uri_user.set_password(new_pass_1)
            uri_user.save()
            #
            if profile_form.cleaned_data['timezone'] != old_tz \
                   and profile_form.cleaned_data['rototill_dates']:
                new_tz = profile_form.cleaned_data['timezone']
                results = rototill_dates(uri_user, old_tz, new_tz)
            return HttpResponseRedirect('/user/%s/' % (uri_user.username))
    return HttpResponse(render('user/profile.html', request=request, user=uri_user, profile_form=profile_form, std=standard_context()))


def BrewForm (user, *args, **kwargs):
    tz = settings.TIME_ZONE
    try:
        tz = user.get_profile().timezone
    except models.UserProfile.DoesNotExist,e:
        pass
    class _BrewForm (forms.ModelForm):
        brew_date = LocalizedDateTimeField(tz, widget=LocalizedDateTimeInput(tz))
        class Meta:
            model = models.Brew
            exclude = ['brewer', 'recipe']
    return _BrewForm(*args, **kwargs)


# sys.stdout = codecs.getwriter('utf-8')(sys.stdout, errors='replace')
def user_brew_new(request, user_name):
    try:
        uri_user = User.objects.get(username__exact = user_name)
    except ObjectDoesNotExist:
        raise Http404
    recipe = None
    form = BrewForm(uri_user)
    if request.method == 'POST':
        if not (request.user.is_authenticated() and request.user == uri_user):
            return HttpResponseForbidden('not allowed')
        form = BrewForm(uri_user, request.POST)
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
        form = BrewForm(uri_user, instance=brew)
    return HttpResponse(render('user/brew/new.html', request=request, user=uri_user, std=standard_context(),
                               recipe=recipe, brew_form=form))


def user_shopping_list(request, user_name):
    try:
        uri_user = User.objects.get(username__exact = user_name)
        # if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    except ObjectDoesNotExist:
        raise Http404
    shopping_list = models.ShoppingList(uri_user)
    return HttpResponse(render('user/shopping-list.html', request=request, user=uri_user, std=standard_context(),
                               shopping_list = shopping_list))
                               

def brew_edit(request, user_name, brew_id):
    '''
    POST /user/jsled/brew/2/edit
    @fixme this is lame.  Make GET an error, use form.is_valid(), integrate with brew(…).
    '''
    try:
        uri_user = User.objects.get(username__exact = user_name)
        # if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
        brew = models.Brew.objects.get(id=brew_id)
        # if not brew: return HttpResponseNotFound('no such brew with id [%d]' % (brew_id))
    except ObjectDoesNotExist:
        raise Http404
    if request.method == 'POST':
        if not (request.user.is_authenticated() and request.user == uri_user):
            return HttpResponseForbidden()
        form = BrewForm(uri_user, request.POST, instance=brew)
        if not form.errors:
            updated_brew = form.save(commit=False)
            updated_brew.id = brew.id
            updated_brew.brewer = brew.brewer
            updated_brew.save()
        else:
            # @fixme handle errors...
            pass
    return HttpResponseRedirect('/user/%s/brew/%d/' % (user_name, updated_brew.id))


def StepForm(user, *args, **kwargs):
    tz = settings.TIME_ZONE
    if user and hasattr(user,'get_profile'):
        try:
            tz = user.get_profile().timezone
        except models.UserProfile.DoesNotExist:
            pass
    class _StepForm (forms.ModelForm):
        notes = forms.CharField(widget=forms.Textarea(), required=False)
        brew = forms.IntegerField(widget=forms.HiddenInput)
        date = LocalizedDateTimeField(tz, widget=LocalizedDateTimeInput(tz))
        class Meta:
            model = models.Step
            exclude = ['gravity']
    return _StepForm(*args, **kwargs)


def brew_post(request, uri_user, brew, step):
    if not (request.user.is_authenticated() and request.user == uri_user):
        return HttpResponseForbidden()
    step_form = StepForm(uri_user, request.POST, instance=step)
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
    brew_form = BrewForm(uri_user, instance=brew)
    recipe_deriv = None
    if brew.recipe:
        recipe_deriv = models.RecipeDerivations(brew.recipe)
    return HttpResponse(render('user/brew/index.html', request=request, std=standard_context(), user=uri_user,
                               brew=brew, steps=steps, step_form=step_form, step_edit=step_edit,
                               brew_form=brew_form, deriv=models.BrewDerivations(brew),
                               recipe_deriv=recipe_deriv))
    

def brew(request, user_name, brew_id, step_id):
    '''
    e.g., /user/jsled/brew/2/[step/3], /user/jsled/brew/2/?type=pitch
    '''
    try:
        uri_user = User.objects.get(username__exact = user_name)
        #if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
        brew = models.Brew.objects.get(id=brew_id)
        #if not brew: return HttpResponseNotFound('no such brew with id [%d]' % (brew_id))
        step = None
        if step_id:
            step = models.Step.objects.get(pk=step_id)
            #if not step:
            #    return HttpResponseNotFound('no such user [%s] brew [%s] step id [%s]' % (user_name, brew_id, step_id))
    except ObjectDoesNotExist:
        raise Http404
    if request.method == 'POST':
        return brew_post(request, uri_user, brew, step)
    # else:
    step_form = None
    step_expand_edit = False
    if step:
        step_form = StepForm(uri_user, instance=step)
        step_expand_edit = True
    if not step_form:
        next_step = None
        next_steps = brew.next_steps()
        explicit_type = request.method == 'GET' and request.GET.has_key('type')
        if explicit_type:
            step_expand_edit = True
            next_step_type = request.GET['type']
            steps = [step for step in next_steps.possible if step.type.id == next_step_type]
            if len(steps) > 0:
                next_step = steps[0]
        else:
            if len(next_steps.possible) > 0:
                next_step = next_steps.possible[0]
        if next_step:
            if next_step.existing_step:
                step_form = StepForm(uri_user, initial={'date': next_step.date or datetime.now()}, instance=next_step.existing_step)
            else:
                step_form = StepForm(uri_user, initial={'brew': brew.id, 'date': next_step.date or datetime.now(), 'type': next_step.type.id})
        else:
            step_form = StepForm(uri_user, initial={'brew': brew.id, 'date': datetime.now()})
    return brew_render(request, uri_user, brew, step_form, step_expand_edit)


class StarForm (forms.ModelForm):
    class Meta:
        model = models.StarredRecipe
        exclude = ['recipe', 'user', 'when']


def user_star(request, user_name):
    try:
        uri_user = User.objects.get(username__exact = user_name)
        #if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    except ObjectDoesNotExist:
        raise Http404
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


def RecipeForm(user, *args, **kwargs):
    tz = settings.TIME_ZONE
    if user and hasattr(user, 'get_profile'):
        try:
            tz = user.get_profile().timezone
        except models.UserProfile.DoesNotExist:
            pass
    class _RecipeForm (forms.ModelForm):
        style = forms.ModelChoiceField(models.Style.objects.all(),
                                       widget=widgets.TwoLevelSelectWidget(choices=get_style_choices()))
        name = forms.CharField(widget=forms.TextInput(attrs={'size': 40}))
        source_url = forms.URLField(required=False, widget=forms.TextInput(attrs={'size': 40}))
        insert_date = LocalizedDateTimeField(tz, widget=LocalizedDateTimeInput(tz), initial=datetime.now())

        class Meta:
            model = models.Recipe
            exclude = ['author', 'derived_from_recipe']
    return _RecipeForm(*args, **kwargs)


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
    def _get_recipe_redirect(recipe):
        return HttpResponseRedirect('/recipe/%d/%s' % (recipe.id, urllib.quote(recipe.name.encode('utf-8'))))
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
    return _get_recipe_redirect(recipe)


def recipe_new(request):
    # uri_user = User.objects.get(username__exact = user_name)
    # if not uri_user: return HttpResponseNotFound('no such user [%s]' % (user_name))
    recipe = None
    recipe_form = RecipeForm(request.user)
    clone_id = None
    if request.method == 'GET' and request.GET.has_key('clone_from_recipe_id'):
        clone_id = request.GET['clone_from_recipe_id']
        to_clone = models.Recipe.objects.get(pk=int(clone_id))
        recipe_form = RecipeForm(request.user, instance=to_clone,
                                 initial={'name': 'Clone of %s' % (to_clone.name),
                                          'derived_from_recipe': to_clone})
    elif request.method == 'POST':
        clone_id = None
        if request.POST.has_key('clone_from_recipe_id') \
           and len(request.POST['clone_from_recipe_id']) > 0:
            clone_id = int(request.POST['clone_from_recipe_id'])
        form = RecipeForm(request.user, request.POST)
        if clone_id:
            to_clone = models.Recipe.objects.get(pk=int(clone_id))
            form = RecipeForm(request.user, request.POST, instance=to_clone)
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
    '''@return (successOrError:boolean, formOrHttpResponse)'''
    if not recipe and recipe_id:
        recipe = models.Recipe.objects.get(pk=recipe_id)
    if request.POST.has_key('item_type'):
        type = request.POST['item_type']
        if type == 'grain':
            return (True,recipe_grain(request, recipe_id))
        elif type == 'hop':
            return (True,recipe_hop(request, recipe_id))
        elif type == 'adjunct':
            return (True,recipe_adjunct(request, recipe_id))
        elif type == 'yeast':
            return (True,recipe_yeast(request, recipe_id))
        else:
            raise Exception('unknown item type [%s]' % (type))
    form = RecipeForm(request.user, request.POST, instance=recipe)
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
    form = kwargs.setdefault('form', RecipeForm(request.user, instance=recipe))
    # @fixme: call something like recipe.grain_list_descending() instead?
    grains = [x for x in models.RecipeGrain.objects.filter(recipe=recipe)]
    hops = [x for x in models.RecipeHop.objects.filter(recipe=recipe)]
    adjuncts = [x for x in models.RecipeAdjunct.objects.filter(recipe=recipe)]
    yeasts = models.RecipeYeast.objects.filter(recipe=recipe)
    #
    def weight_comparator(a,b):
        a_has_amount = a.amount_value and a.amount_units
        b_has_amount = b.amount_value and b.amount_units
        if not a_has_amount or not b_has_amount:
            if not a_has_amount:
                return -1
            return 1
        def to_grams(amount):
            return models.convert_weight(amount.amount_value, amount.amount_units, 'gr')
        def safe_to_grams(amount):
            try:
                return to_grams(amount)
            except:
                return 0
        a_in_grams,b_in_grams = tuple([safe_to_grams(x) for x in [a,b]])
        rtn = int(a_in_grams - b_in_grams)
        if rtn == 0:
            rtn = a.id - b.id
        return rtn
    def invert_comparator(cmp):
        return lambda a,b: -cmp(a,b)
    for x in grains, hops, adjuncts:
        x.sort(cmp=invert_comparator(weight_comparator))
    #
    grain_form = kwargs.setdefault('grain_form', RecipeGrainForm())
    hop_form = kwargs.setdefault('hop_form', RecipeHopForm())
    adj_form = kwargs.setdefault('adj_form', RecipeAdjunctForm())
    yeast_form = kwargs.setdefault('yeast_form', RecipeYeastForm())
    derivations = models.RecipeDerivations(recipe)
    return HttpResponse(render('recipe/view.html', request=request, std=standard_context(),
                               recipe=recipe, grains=grains, hops=hops, adjuncts=adjuncts, yeasts=yeasts,
                               recipe_form=form,
                               grain_form=grain_form,
                               hop_form=hop_form,
                               adj_form=adj_form,
                               yeast_form=yeast_form,
                               deriv=derivations
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
    try:
        recipe = models.Recipe.objects.get(pk=recipe_id)
    except ObjectDoesNotExist:
        raise Http404
    return _render_recipe(request, recipe)


class EfficiencyTracker (object):
    def __init__(self, user):
        self._user = user
        self._brews = list(models.Brew.objects.filter(brewer__exact = user).order_by('-brew_date')[0:10])
        self._brews.reverse()
        self._derivations = [models.BrewDerivations(brew) for brew in self._brews]
        self._derivations = [d for d in self._derivations if not d.can_not_derive_efficiency()]

    def has_data(self):
        return len(self._derivations) > 1

    def url(self):
        url = 'http://chart.apis.google.com/chart?chs=400x100&cht=lc'
        # url += '&chds=0,100'
        efficiencies_dates = [{'efficiency': '%0.2f' % (derived.efficiency()), 'date': safe_datetime_fmt_raw(derived._brew.brew_date, '%m/%d', self._user)}
                              for derived
                              in self._derivations
                              if not derived.can_not_derive_efficiency()]
        csv = ','.join([x['efficiency'] for x in efficiencies_dates])
        url += '&chd=t:%s' % (csv)
        url += '&chxt=x,r'
        url += '&chxl=0:|' + '|'.join([x['date'] for x in efficiencies_dates])
        url += '&chm=N*f1*,000000,0,-1,10'
        return url
