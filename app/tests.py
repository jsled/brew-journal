# -*- encoding: utf-8 -*-

# Copyright (c) 2008-2010, Joshua Sled <jsled@asynchronous.org>
# See LICENSE file for "New BSD" license details.

import datetime
import decimal
import itertools
import re
import unittest

from django.contrib import auth
from django.test.client import Client
from django.test import TestCase
from brewjournal.app import models, views


class AppTestCase (TestCase):
    fixtures = ['auth', 'grains1', 'grains2', 'grains3', 'hops0', 'hops1', 'yeasts1', 'adjuncts', 'yeast-manufacturers', 'yeasts', 'styles']

    def create_recipe(self, name, date, style, hops, grains):
        res = self.client.post('/recipe/new/', {'name': name, 'insert_date': date, 'batch_size': 5, 'batch_size_units': 'gl', 'boil_length': 60, 'efficiency': 66, 'style': style, 'type': 'a'})
        self.assertEquals(302, res.status_code, res)
        recipe_url = res['Location']
        recipe_base_url = '/'.join(recipe_url.split('/')[3:-1])
        hop_post_url = '/%s/' % (recipe_base_url)
        for hop,amt,units,boil_time in hops:
            args = {'item_type': 'hop', 'hop': hop, 'amount_value': amt, 'amount_units': units, 'usage_type': 'boil', 'boil_time': boil_time}
            res = self.client.post(hop_post_url, args)
            self.assertEqual(302, res.status_code, '%d %s' % (res.status_code, res))
        grain_post_url = '/%s/' % (recipe_base_url)
        for grain,amt,units in grains:
            res = self.client.post(grain_post_url, {'item_type': 'grain', 'grain': grain, 'amount_value': amt, 'amount_units': units})
            self.assertEqual(302, res.status_code, res)
        return recipe_base_url

    def create_brew(self, user, recipe_id, date, steps):
        brew_res = self.client.post('/user/%s/brew/new/' % (user), {'recipe_id': recipe_id, 'brew_date': date})
        self.assertEquals(302, brew_res.status_code)
        brew_url = '/'.join(brew_res['Location'].split('/')[3:])
        brew_id = int(brew_url.split('/')[-1])
        for fields in steps:
            fields.setdefault('brew', brew_id)
            post_url = '/%s/' % (brew_url)
            res = self.client.post(post_url, fields)
            self.assertEquals(302, res.status_code, 'posting to %s %s: %s' % (post_url,fields,res))
        return brew_url


class BasicLoginTest (AppTestCase):

    def testFailed(self):
        res = self.client.post('/', {'username': 'bob', 'password': '', 'sub': 'login'})
        self.assertEqual(200, res.status_code)
        # @fixme: add form content check

    def testLogin(self):
        res = self.client.post('/', {'username': 'jsled', 'password': 's3kr1t', 'sub': 'login'})
        self.assertRedirects(res, '/user/jsled/')

    def testDjangoLogin(self):
        self.assertTrue(self.client.login(username='jsled', password='s3kr1t'))


class NotLoggedInMeansNoActions (TestCase):
    fixtures = ['auth']

    def testUserPage(self):
        res = self.client.get('/user/jsled/')
        # @fixme: what is this character indicative of??
        self.assertNotContains(res, u'»', status_code=200)


class HopWithoutBoilTime (AppTestCase):
    def test(self):
        app = self.client
        self.assertTrue(app.login(username='jsled', password='s3kr1t'))
        res = app.post('/recipe/new/', {'name': 'test', 'insert_date': '2008-08-31 20:48', 'batch_size': 5, 'batch_size_units': 'gl',
                                        'boil_length': 60, 'efficiency': 66, 'style': 1, 'type': 'a'})
        self.assertEqual(302, res.status_code, '%d: %s' % (res.status_code,res.content))
        new_recipe_url = res['Location']
        base_recipe_url = '/'.join(new_recipe_url.split('/')[3:-1])
        hop_post_url = '/%s/' % (base_recipe_url)
        res = app.post(hop_post_url, {'item_type': 'hop', 'hop': 1, 'amount_value': 2, 'amount_units': 'oz'})
        # @fixme:
        #assert(res.body.contains validation error mumble on boil-time field)
        self.assertEqual(200, res.status_code)


class ShoppingListViewTest (AppTestCase):
    def test(self):
        from datetime import datetime, timedelta
        app = self.client
        user,passwd = 'jsled', 's3kr1t'
        app.login(username=user, password=passwd)
        # recipe A with 1 unique grain, 1 shared grain, 1 unique hop, 1 shared hop
        # recipe B with 1 unique grain, 1 shared grain, 1 unique hop, 1 shared hop
        recipe_a = self.create_recipe('test a', '2008-12-26 08:32', 1,
                                      [(1, 1, 'oz', 30), (2, 2, 'oz', 60)],
                                      [(1, 1, 'lb'), (2, 2, 'lb')])
        recipe_b = self.create_recipe('test b', '2008-12-26 08:32', 2,
                                      [(1, 1, 'oz', 15), (3, 3, 'oz', 60)],
                                      [(1, 1, 'lb'), (3, 3, 'lb')])
        recipe_c = self.create_recipe('test c', '2008-12-26 08:32', 3,
                                      [(4, 20, 'oz', 60)],
                                      [(4, 20, 'lb')])
        recipe_a_id = int(recipe_a.split('/')[-1])
        recipe_b_id = int(recipe_b.split('/')[-1])
        recipe_c_id = int(recipe_c.split('/')[-1])
        #
        now = datetime.now()
        now = now.replace(microsecond=0)
        tomorrow = now + timedelta(1) # day
        yesterday = now - timedelta(1)
        self.create_brew(user, recipe_a_id, tomorrow, [{'type': 'strike', 'entry_date': str(now), 'date': str(tomorrow), 'gravity_read_type': 'sg'}])
        self.create_brew(user, recipe_b_id, tomorrow, [{'type': 'buy', 'entry_date': str(now), 'date': str(tomorrow), 'gravity_read_type': 'sg'}])
        self.create_brew(user, recipe_c_id, yesterday, [{'type': 'buy', 'entry_date': str(yesterday), 'date': str(now), 'gravity_read_type': 'sg'}])
        # 
        res = app.get('/user/%s/shopping/' % (user))
        self.assertEquals(200, res.status_code)
        try:
            self.assertNotContains(res, u'test a', 200)
            self.assertContains(res, u'test b')
            self.assertNotContains(res, u'test c', 200)
            self.assertContains(res, u'1 oz', count=1)
            self.assertNotContains(res, u'2 oz', 200)
            self.assertContains(res, u'3 oz', count=1)
            self.assertContains(res, u'1 lb', count=1)
            self.assertNotContains(res, u'2 lb', 200)
            self.assertContains(res, u'3 lb', count=1)
            self.assertNotContains(res, u'20 oz', 200)
            self.assertNotContains(res, u'20 lb', 200)
            # @fixme: more appropriate assertions
        except Exception,e:
            print res
            raise e
                          

# @fixme:
# - creating a recipe
#   - adding items to a recipe
#   - changing a recipe
# - creating a brew from a recipe
#   - adding steps to the brew

class NewUserTest (TestCase):
    def testNewUserInvalidUsername(self):
        res = self.client.post('/', {'sub': 'create', 'username': '', 'password': '', 'password_again': '', 'email': ''})
        import re
        assertion = re.compile(r'This field is required', re.IGNORECASE)
        matches = assertion.search(str(res))
        self.assertTrue(matches)
        # self.assertFormError(res, 'RegisterForm', …
        
    def testNewUserInvalidNoPassword(self):
        res = self.client.post('/', {'sub': 'create', 'username': 'foo', 'password': '', 'password_again': '', 'email': ''})
        self.assertContains(res, 'Matching passwords required')

    def testMismatchedPasswords(self):
        res = self.client.post('/', {'sub': 'create', 'username': 'novelUsername', 'password': 'foo', 'password_again': 'bar'})
        self.assertContains(res, 'Matching passwords required')

    def testEmptyEmail(self):
        res = self.client.post('/', {'sub': 'create', 'username': 'novelUsername', 'password': 'foo', 'password_again': 'foo', 'email': ''})
        self.assertContains(res, 'Must have valid email')

    def testInvalidEmail(self):
        res = self.client.post('/', {'sub': 'create', 'username': 'novelUsername', 'password': 'foo', 'password_again': 'foo', 'email': 'lol cat @ lolhost.zomg'})
        self.assertContains(res, 'Must have valid email')

    def testValidNewUser(self):
        res = self.client.post('/', {'sub': 'create', 'username': 'novelUsername', 'password': 'foo', 'password_again': 'foo', 'email': 'user@validhost.com'})
        self.assertRedirects(res, '/user/novelUsername/profile')

    def testInvalidExistingUsername(self):
        res = self.client.post('/', {'sub': 'create', 'username': 'novelUsername', 'password': 'foo', 'password_again': 'foo', 'email': 'user@validhost.com'})
        self.assertRedirects(res, '/user/novelUsername/profile')
        self.client.logout()
        res2 = self.client.post('/', {'sub': 'create', 'username': 'novelUsername', 'password': 'foo', 'password_again': 'foo', 'email': 'user@validhost.com'})
        self.assertContains(res2, 'Username [novelUsername] is unavailable')
        

class BrewDerivationsTest (TestCase):
    def testNoAbvComputation(self):
        brew = models.Brew()
        derivs = models.BrewDerivations(brew)
        cannot = derivs.can_not_derive_abv()
        self.assertTrue(len(cannot) > 0, len(cannot))
        self.assertEquals(2, len(cannot))

    def testMultiStepAbvComputation(self):
        brew = Mock(step_set=FkSet([Mock(type='boil-start', gravity=decimal.Decimal('1.049')),
                                    Mock(type='pitch', gravity=decimal.Decimal('1.064')),
                                    Mock(type='keg', gravity=decimal.Decimal('1.022'))]))
        derivs = models.BrewDerivations(brew)
        abv = derivs.alcohol_by_volume()
        self.assert_(abv > decimal.Decimal('3.645'), str(abv))
        self.assertEquals(abv, decimal.Decimal('5.67'), str(abv))

    def testNoEfficiencyComputations(self):
        brew = models.Brew(recipe=models.Recipe())
        derivs = models.BrewDerivations(brew)
        cannot = derivs.can_not_derive_efficiency()
        self.assertTrue(len(cannot) > 0, len(cannot))
        self.assertEquals(2, len(cannot))

    def testAttenuationComputation(self):
        brew = Mock(step_set=FkSet([Mock(type='pitch', gravity=decimal.Decimal('1.070')),
                                    Mock(type='keg', gravity=decimal.Decimal('1.015'))]))
        derivs = models.BrewDerivations(brew)
        aa = derivs.apparent_attenuation()
        self.assert_(aa - decimal.Decimal('78.57') < decimal.Decimal('0.1'))


class Test404s (AppTestCase):
    fixtures = ['auth']

    def _assert404(self, url):
        res = self.client.get(url)
        self.assertEquals(404, res.status_code)

    def testUser404(self):
        self._assert404('/user/does_not_exist')

    def testUserProfile404(self):
        self._assert404('/user/does_not_exist/profile')

    def testUser404NewBrew(self):
        self._assert404('/user/does_not_exist/brew/new')

    def testUser404Shopping(self):
        self._assert404('/user/does_not_exist/shopping')

    def testUserBrew404(self):
        self.client.post('/', {'username': 'jsled', 'password': 's3kr1t', 'sub':' login'})
        self._assert404('/user/jsled/brew/10000')

    # @add: /user/exists/brew/exists/step/does_not_exist

    def testRecipe404(self):
        self._assert404('/recipe/129083450/')
        self._assert404('/recipe/129083450/Testing')


class TestLogin (AppTestCase):
    fixtures = ['auth']

    def testLogin(self):
        res = self.client.post('/', {'username': 'jsled', 'password': 's3kr1t', 'sub': 'login'})
        self.assertEquals(302, res.status_code)
        new_url = '/' + '/'.join(res['Location'].split('/')[3:])
        res = self.client.get(new_url)
        self.assertContains(res, 'sign out', status_code=200)

    def testInvalidLogin(self):
        res = self.client.post('/', {'username': 'jsled', 'password': 'foobar', 'sub': 'login'})
        self.assertNotContains(res, 'sign out', 200)
        self.assertContains(res, 'invalid username or password', status_code=200)

    # @add testDisabledAccount


class TestReg (AppTestCase):
    fixtures = ['auth']

    def testBrokenReg(self):
        res = self.client.post('/', {'sub': 'create', 'username': 'bill', 'password': 'foo', 'password_again': 'bar', 'email': 'invalid'})
        self.assertContains(res, 'Matching passwords required', status_code=200)
        self.assertContains(res, 'valid e-mail address', status_code=200)

    def testSuccessfulReg(self):
        passwd = 'foo'
        res = self.client.post('/', {'sub': 'create', 'username': 'bill', 'password': passwd, 'password_again': passwd, 'email': 'jsled@asynchronous.org'})
        self.assertEquals(302, res.status_code)
        self.assertTrue(res['Location'].index('profile') != -1)

    def testExistingUsername(self):
        passwd = 'foo'
        res = self.client.post('/', {'sub': 'create', 'username': 'jsled', 'password': passwd, 'password_again': passwd, 'email': 'jsled@asynchronous.org'})
        self.assertContains(res, 'is unavailable', status_code=200)

    # @add: testUnknownSubmitType


class Mock (object):
    def __init__(self, **kwargs):
        for k,v in kwargs.iteritems():
            self.__dict__[k] = v

class FkSet (object):
    def __init__(self, list = None):
        if not list: list = []
        self._items = list

    def all(self):
        return self._items

    def count(self):
        return len(self._items)


class ShoppingListTest (TestCase):

    def test(self):
        import random
        grains = [Mock(name='g%d' % (i)) for i in range(10)]
        rgrains = [Mock(grain=g, amount_value=1, amount_units='lbs') for g in grains]
        hops = [Mock(name='h%d' % (i)) for i in range(10)]
        rhops = [Mock(hop=h, amount_value=1, amount_units='oz') for h in hops]
        #
        r1_grains = random.sample(rgrains, 5)
        r1_hops = random.sample(rhops, 5)
        r1 = Mock(recipegrain_set = FkSet(r1_grains),
                  recipehop_set = FkSet(r1_hops),
                  recipeyeast_set = FkSet(),
                  recipeadjunct_set = FkSet())
        r2 = Mock(recipegrain_set = FkSet(rgrains),
                  recipehop_set = FkSet(rhops),
                  recipeyeast_set = FkSet(),
                  recipeadjunct_set = FkSet())
        b1 = Mock(recipe=r1)
        b2 = Mock(recipe=r1)
        b3 = Mock(recipe=r2)
        #
        groceries = models.ShoppingList(pre_brews=[b1, b2, b3])
        self.assertEquals(10, len(groceries.grains))
        self.assertEquals(10, len(groceries.hops))
        for grain,brews in groceries.grains:
            self.assertTrue(len(brews) <= 3)
        for hop,brews in groceries.hops:
            self.assertTrue(len(brews) <= 3)

class MockUser (Mock):
    def __init__(self, profile, **kwargs):
        self.profile = profile
        super(MockUser, self).__init__(**kwargs)

    def get_profile(self):
        return self.profile


class MockProfile (Mock):
    def __init__(self, **kwargs):
        super(MockProfile, self).__init__(**kwargs)

    def __getitem__(self, key):
        return self.__dict__.get(key, None)


class MockStep (models.Step, Mock):
    def __init__(self, **kwargs):
        Mock.__init__(self, **kwargs)


def fake_datetime(timestamp):
    # http://ericholscher.com/blog/2008/aug/14/using-mock-objects-django-and-python-testing/
    class MockDatetime (datetime.datetime):
        @classmethod
        def now(cls):
            return datetime.datetime.fromtimestamp(timestamp)
    return MockDatetime


class RecipeFormTest (AppTestCase):
    
    def testEfficiency(self):
        user = auth.models.User.objects.get(username='jsled')
        profile = user.get_profile()
        profile.pref_brewhouse_efficiency = 20
        profile.save()

        style = models.Style.objects.get(id=1)
        recipe = models.Recipe(author=user, name='test', batch_size=5, batch_size_units='gl', efficiency=30, style=style)

        form = views.RecipeForm(user, None, instance=recipe)
        inputHtml = str(form['efficiency'])
        self.assertTrue(inputHtml.rfind('value="30"') != -1)

class NextStepsTest (TestCase):
    def testBasic(self):
        profile = MockProfile()
        user = MockUser(profile)
        recipe = Mock(type='e')
        brew = Mock(brewer=user, recipe=recipe, last_state=None, step_set=FkSet([]))
        next_step_gen = models.NextStepGenerator(brew)
        next_steps = next_step_gen.get_next_steps()
        self.assertTrue(len(next_steps.possible) == 2)
        possible_types = [s.type.id for s in next_steps.possible]
        self.assertTrue('steep' in possible_types, next_steps)
        self.assertTrue('boil-start' in possible_types, next_steps)
        #
        all_grain_recipe = Mock(type='a')
        brew = Mock(brewer=user, recipe=all_grain_recipe, last_state=None, step_set=FkSet([]))
        next_steps = models.NextStepGenerator(brew).get_next_steps()
        self.assertTrue(len(next_steps.possible) == 1, next_steps)
        possible_types = [s.type.id for s in next_steps.possible]
        self.assertTrue('strike' in possible_types)
        #
        profile = MockProfile(pref_make_starter=True)
        user = MockUser(profile)
        brew = Mock(brewer=user, recipe=recipe, last_state=None, step_set=FkSet([]))
        next_step_gen = models.NextStepGenerator(brew)
        next_steps = next_step_gen.get_next_steps()
        self.assertTrue(len(next_steps.possible) == 3)
        possible_types = [s.type.id for s in next_steps.possible]
        for asserted in ['steep', 'boil-start', 'starter']:
            self.assertTrue(asserted in possible_types, '%s, looking for %s' % (next_steps, asserted))

    def testEndStage(self):
        profile = MockProfile(pref_dispensing_style='k')
        user = MockUser(profile)
        recipe = Mock(type='a')
        steps = [MockStep(id=1, type='ferm1', date=datetime.datetime.fromtimestamp(1), entry_date=datetime.datetime.fromtimestamp(1))]
        brew = Mock(brewer=user, recipe=recipe, last_state='ferm1', step_set=FkSet(steps))
        next_steps = models.NextStepGenerator(brew).get_next_steps()
        possible_types = [step.type.id for step in next_steps.possible]
        maybe_types = [step.type.id for step in next_steps.maybe]
        self.assertTrue('keg' in possible_types, str(next_steps))
        self.assertTrue('consumed' not in possible_types, str(next_steps))
        self.assertTrue('bottle' in maybe_types, str(next_steps))
        
    def testFuture(self):
        profile = MockProfile()
        user = MockUser(profile)
        steps = [MockStep(id=1, type='strike', entry_date=datetime.datetime.fromtimestamp(5), date=datetime.datetime.fromtimestamp(105)),
                 MockStep(id=2, type='dough', entry_date=datetime.datetime.fromtimestamp(6), date=datetime.datetime.fromtimestamp(106)),
                 MockStep(id=3, type='mash', entry_date=datetime.datetime.fromtimestamp(7), date=datetime.datetime.fromtimestamp(107)),
                 MockStep(id=4, type='boil-start', entry_date=datetime.datetime.fromtimestamp(10), date=datetime.datetime.fromtimestamp(110)),
                 MockStep(id=5, type='pitch', entry_date=datetime.datetime.fromtimestamp(20), date=datetime.datetime.fromtimestamp(120))]

        saved_datetime = datetime.datetime
        datetime.datetime = fake_datetime(30)
        # + with
        for recipe_type in ('a', 'e'):
            recipe = Mock(type=recipe_type)
            brew = Mock(brewer=user, recipe=recipe, last_state=None, step_set=FkSet(steps))
            next_steps = models.NextStepGenerator(brew).get_next_steps()
            for step in next_steps.possible:
                next_step_type_in_defined_steps = step.type.id in [s.type for s in steps]
                if next_step_type_in_defined_steps:
                    self.assertTrue(step.existing_step)
            possible_types = [s.type.id for s in next_steps.possible]
            to_assert = {'a': ['strike'],
                         'e': ['steep', 'boil-start']}[recipe_type]
            self.assertTrue(len(next_steps.possible) == len(to_assert),
                            'expecting %d items in %s for type %s' % (len(to_assert), next_steps, recipe_type))
            for asserted in to_assert:
                self.assertTrue(asserted in possible_types, '%s asserted %s' % (next_steps, asserted))
        datetime.datetime = saved_datetime
        # - with

        # + with
        saved_datetime = datetime.datetime
        datetime.datetime = fake_datetime(125)
        steps[0].date = datetime.datetime.fromtimestamp(125)
        recipe = Mock(type='a')
        brew = Mock(brewer=user, recipe=recipe, last_state='strike', step_set=FkSet(steps))
        next_steps = models.NextStepGenerator(brew).get_next_steps()
        self.assertTrue(len(next_steps.possible) == 2, next_steps)
        for next_step,expected_type in itertools.izip(next_steps.possible, ['dough', 'mash']):
            # @fixme: of course, these are wrong given how we really want future-dated steps to work.
            self.assertTrue(next_step.type.id == expected_type, next_step)
            self.assertTrue(next_step.date == datetime.datetime.fromtimestamp(125), next_step)
        # - with
        datetime.datetime = saved_datetime


class TestTimezoneAdjustments (AppTestCase):
    def testRecipe(self):
        user,passwd = 'jsled','s3kr1t'
        self.client.login(username=user,password=passwd)
        #
        profile = models.UserProfile.objects.get(user__username='jsled')
        profile.timezone = 'US/Eastern'
        profile.save()
        #
        now = datetime.datetime.now()
        pattern = '%Y-%m-%d %H:%M:%S'
        now_str = now.strftime(pattern)
        unused_style = 1
        recipe_url = self.create_recipe('test', now_str, unused_style, [], [])
        recipe_url = '/' + recipe_url + '/'  # @fixme: quick fix; do this globally
        #
        res = self.client.get(recipe_url)
        date_pattern = re.compile(r'''name="insert_date" value="([^"]+)"''')
        date_eastern_str = date_pattern.search(res.content).group(1)
        date_eastern = datetime.datetime.strptime(date_eastern_str, pattern)
        profile.timezone = 'US/Pacific'
        profile.save()
        res2 = self.client.get(recipe_url)
        date_pacific_str = date_pattern.search(res2.content).group(1)
        date_pacific = datetime.datetime.strptime(date_pacific_str, pattern)
        #
        delta = date_eastern - date_pacific
        MINUTE_SECONDS = 60
        HOUR_SECONDS = 60 * MINUTE_SECONDS
        self.assertEqual(3 * HOUR_SECONDS, delta.seconds)
        #
        # @fixme: assert recipe model insert_date unchanged
        #
        # plus 30 minutes
        new_time = date_pacific + datetime.timedelta(seconds = 30 * MINUTE_SECONDS)
        new_time_str = new_time.strftime(pattern)
        res3 = self.client.post(recipe_url, {'name':'test', 'batch_size': '5', 'batch_size_units': 'gl', 'boil_length': 60, 'efficiency': 75, 'style': 1, 'type': 'a', 'insert_date': new_time_str})
        self.assertEquals(302, res3.status_code)
        res3 = self.client.get(recipe_url)
        updated_pacific_str = date_pattern.search(res3.content).group(1)
        updated_pacific = datetime.datetime.strptime(updated_pacific_str, pattern)
        self.assertEquals(new_time, updated_pacific)
        #
        profile.timezone = 'US/Eastern'
        profile.save()
        res4 = self.client.get(recipe_url)
        updated_eastern_str = date_pattern.search(res4.content).group(1)
        updated_eastern = datetime.datetime.strptime(updated_eastern_str, pattern)
        updated_delta = updated_eastern - updated_pacific
        self.assertEqual(3 * HOUR_SECONDS, updated_delta.seconds)

    # def testBrew():


class RecipeSortedIngredients (AppTestCase):
    def testInsertedOutOfOrderButStillSorted(self):
        user,passwd = 'jsled', 's3kr1t'
        self.client.login(username=user, password=passwd)
        
        hop_1,hop_2 = tuple([models.Hop.objects.get(pk=x) for x in [1,2]])
        grain_1,grain_2,grain_3,grain_4 = tuple([models.Grain.objects.get(pk=x) for x in [1,2,3,4]])
        recipe_url = self.create_recipe('foo', '2009-08-02', 1,
                                        [(hop_1.id, 1, 'oz', 30), (hop_2.id, 2, 'oz', 60)],
                                        [(grain_1.id, 1, 'lb'), (grain_2.id, 2, 'lb'), (grain_3.id, 3, 'ct'), (grain_4.id, '0.125', 'tsp')])
        res = self.client.get('/' + recipe_url + '/')
        #
        body = res.content.decode('utf-8')
        grain_1_idx = body.find(grain_1.name)
        grain_2_idx = body.find(grain_2.name)
        grain_3_idx = body.find(grain_3.name)
        grain_4_idx = body.find(grain_4.name)
        self.assertTrue(grain_1_idx != -1)
        self.assertTrue(grain_2_idx != -1)
        self.assertTrue(grain_3_idx != -1)
        self.assertTrue(grain_4_idx != -1)
        self.assertTrue(grain_2_idx < grain_1_idx)
        self.assertTrue(grain_3_idx > grain_1_idx)
        self.assertTrue(grain_4_idx > grain_1_idx)
        self.assertTrue(grain_4_idx > grain_2_idx)
        self.assertTrue(grain_4_idx > grain_3_idx)
        #
        hop_1_idx = body.find(hop_1.name)
        hop_2_idx = body.find(hop_2.name)
        self.assertTrue(hop_1_idx != -1)
        self.assertTrue(hop_2_idx != -1)
        self.assertTrue(hop_2_idx < hop_1_idx)

    #def testUpdatedItemsGetResorted(self):


class FutureStepsTest (AppTestCase):

    def testComingOfAge(self):
        saved_datetime = datetime.datetime

        # +with
        datetime.datetime = fake_datetime(30)
        user = auth.models.User()
        user.save()
        brew = models.Brew()
        brew.brewer = user
        brew.save()
        futureStep = models.Step()
        futureStep.brew = brew
        futureStep.type = 'buy'
        futureStep.date = datetime.datetime.fromtimestamp(130)
        futureStep.entry_date = datetime.datetime.fromtimestamp(30)
        futureStep.save()
        steps = models.Step.objects.future_steps_for_user(user)
        self.assertTrue(steps.count() == 1)
        brews = models.Brew.objects.brews_with_future_steps(user)
        self.assertTrue(brews.count() == 1)
        # -with
        # +with
        datetime.datetime = fake_datetime(150)
        steps = models.Step.objects.future_steps_for_user(user)
        self.assertTrue(steps.count() == 0)
        brews = models.Brew.objects.brews_with_future_steps(user)
        self.assertTrue(brews.count() == 0)
        # -with
        datetime.datetime = saved_datetime


class StepTimeShiftTest (AppTestCase):

    def setUp(self):
        now = datetime.datetime.now()
        now = now - datetime.timedelta(microseconds=now.microsecond)
        self.now = now
        self.now_plus_5 = now + datetime.timedelta(minutes=5)
        self.now_plus_10 = now + datetime.timedelta(minutes=10)
        self.now_plus_15 = now + datetime.timedelta(minutes=15)
        self.now_plus_20 = now + datetime.timedelta(minutes=20)

        self.user = auth.models.User()
        self.user.save()

        self.brew = models.Brew()
        self.brew.brewer = self.user
        self.brew.save()

        self.strike = models.Step(brew=self.brew, type='strike', date=self.now)
        self.strike.save()

        self.dough = models.Step(brew=self.brew, type='dough', date=self.now_plus_5)
        self.dough.save()

        self.mash = models.Step(brew=self.brew, type='mash', date=self.now_plus_10)
        self.mash.save()

        self.first_run = models.Step(brew=self.brew, type='batch1-start', date=self.now_plus_15)
        self.first_run.save()

    def testBasicShift(self):
        dough2 = models.Step.objects.get(pk=self.dough.id)
        dough2.date = self.now_plus_10
        self.brew.shift_steps(#self.dough,
            dough2)

        for step in self.brew.step_set.all():
            if step.type == 'strike':
                self.assertEquals(self.now, step.date)
            elif step.type == 'dough':
                self.assertEquals(self.now_plus_10, step.date)
            elif step.type == 'mash':
                self.assertEquals(self.now_plus_15, step.date)
            elif step.type =='batch1-start':
                self.assertEquals(self.now_plus_20, step.date)
            else:
                self.fail('unknown type %s' % (step.type))

    def testFarFutureNonShift(self):
        two_weeks_away = self.now + datetime.timedelta(weeks=2)
        future_keg = models.Step(brew=self.brew, type='keg', date=two_weeks_away)
        future_keg.save()

        strike2 = models.Step.objects.get(pk=self.strike.id)
        strike2.date = self.now_plus_20
        self.brew.shift_steps(#self.strike,
            strike2)

        upd_keg = self.brew.step_set.get(type='keg')
        self.assertEqual(two_weeks_away, upd_keg.date)


#class BrewViewTest (AppTestCase):

    # brew has no steps:
    #   next-step = 'starter' or something
    #   with type=boil-start, next-step = boil-start
    # brew has future steps:
    #   brew has relevant future steps:
    #       no ?type: next-step =
    # brew is "complete", has no future steps


class UtilTest (TestCase):
    def testUtil(self):
        import doctest
        doctest.testmod(models)

    def testWeightConversionRoundTripping(self):
        convertible = ['gr', 'kg', 'oz', 'lb']
        import random
        for from_units in convertible:
            for to_units in convertible:
                for x in range(10):
                    val = decimal.Decimal(str(random.random() * 100))
                    converted = models.convert_weight(val, from_units, to_units)
                    round_tripped = models.convert_weight(converted, to_units, from_units)
                    self.assertAlmostEqual(val, round_tripped, 2)

    def testVolumeConversion(self):
        self.assertAlmostEqual(decimal.Decimal('1'), models.convert_volume(16, 'c', 'gl'), 2)
        self.assertAlmostEqual(decimal.Decimal('5.01928'), models.convert_volume(19000, 'ml', 'gl'), 2)
        self.assertAlmostEqual(decimal.Decimal('18.93'), models.convert_volume(5, 'gl', 'l'), 2)

    def testVolumeConversionRoundTripping(self):
        convertible = ['c', 'q', 'gl', 'ml', 'l'] # , 'tsp', 'tbsp', 'pt'
        import random
        for from_units in convertible:
            for to_units in convertible:
                for x in range(10):
                    random_val = decimal.Decimal(str(random.random() * 100))
                    converted = models.convert_volume(random_val, from_units, to_units)
                    round_tripped = models.convert_volume(converted, to_units, from_units)
                    self.assertAlmostEqual(random_val, round_tripped, 1,
                                           'from %s %s to %s %s back to %s %s'
                                           % (random_val, from_units, converted,
                                              to_units, round_tripped, from_units))


class StepTest (TestCase):
    def testGravityCorrection(self):
        s = models.Step()
        s.gravity_read = decimal.Decimal('1.070')
        s.gravity_read_temp_units = 'f'
        s.gravity_read_temp = 70
        self.assertEquals(decimal.Decimal('1.071'), s.gravity)
        
    def testGravitySet(self):
        s = models.Step()
        s.gravity = decimal.Decimal('1.040')
        self.assertEquals(decimal.Decimal('1.040'), s.gravity)
        self.assertEquals(decimal.Decimal('1.040'), s.gravity_read)
        self.assertEquals('f', s.gravity_read_temp_units)
        self.assertEquals(59, s.gravity_read_temp)

class RecipeDerivationsTest (TestCase):

    fixtures = ['hops0', 'grains1', 'grains3']

    def assertPercentageSum(self, thingies):
        percentage_accum = decimal.Decimal('0')
        for thingy in thingies:
            percentage_accum += thingy.percentage
        self.assertAlmostEquals(decimal.Decimal('100'), percentage_accum, 1)

    def testBareRecipe(self):
        bare_recipe = Mock()
        deriv = models.RecipeDerivations(bare_recipe)
        #
        reasons = deriv.can_not_derive_og()
        self.assertEquals(3, len(reasons))
        for expected_substring in ['non-zero batch', 'batch size', 'grains']:
            for reason in reasons:
                if reason.find(expected_substring) != -1:
                    break
            else:
                self.fail('did not contain expected-substring [%s] reason' % (expected_substring))
        #
        ibu_reasons = deriv.can_not_derive_ibu()
        self.assertEquals(3, len(ibu_reasons))
        for expected_substring in ['non-zero batch', 'batch size', 'hops']:
            for reason in ibu_reasons:
                if reason.find(expected_substring) != -1:
                    break
            else:
                self.fail('did not contain expected-substring [%s] reason' % (expected_substring))

    def testBasicIbus(self):
        perle = models.Hop.objects.get(name__exact='Perle (US)')
        liberty = models.Hop.objects.get(name__exact='Liberty')
        hops = [models.RecipeHop(hop=perle, boil_time=60, amount_value=decimal.Decimal('1.5'), amount_units='oz'),
                models.RecipeHop(hop=liberty, boil_time=15, amount_value=decimal.Decimal('1'), amount_units='oz')]
        recipe = Mock(batch_size=5, batch_size_units='gl', recipehop_set=FkSet(hops))
        deriv = models.RecipeDerivations(recipe)
        no_reasons = deriv.can_not_derive_ibu()
        self.assertEquals([], no_reasons)
        ibus = deriv.compute_ibu(decimal.Decimal('1.080'))
        self.assertAlmostEquals(decimal.Decimal('37'), ibus.average, 0)

    def testBasicIbusOverride(self):
        # this is straight from http://www.howtobrew.com/section1/chapter5-5.html
        dec = lambda x : decimal.Decimal(x)
        perle = models.Hop.objects.get(name__exact='Perle (US)')
        liberty = models.Hop.objects.get(name__exact='Liberty')
        hops = [models.RecipeHop(hop=perle, boil_time=60, amount_value=dec('1.5'), amount_units='oz', aau_override=dec('6.4')),
                models.RecipeHop(hop=liberty, boil_time=15, amount_value=dec('1'), amount_units='oz', aau_override=dec('4.6'))]
        recipe = Mock(batch_size=5, batch_size_units='gl', recipehop_set=FkSet(hops))
        deriv = models.RecipeDerivations(recipe)
        no_reasons = deriv.can_not_derive_ibu()
        self.assertEquals([], no_reasons)
        ibus = deriv.compute_ibu(decimal.Decimal('1.080'))
        self.assertAlmostEquals(decimal.Decimal('32'), ibus.average, 0)

    def testRealWorldIbus(self):
        chinook = models.Hop.objects.get(name__exact='Chinook')
        golding = models.Hop.objects.get(name__exact='Golding (US)')
        hops = [models.RecipeHop(hop=chinook, boil_time=90, amount_value=decimal.Decimal('2'), amount_units='oz'),
                models.RecipeHop(hop=golding, boil_time=90, amount_value=decimal.Decimal('1'), amount_units='oz')]
        recipe = Mock(batch_size=5, batch_size_units='gl', recipehop_set=FkSet(hops))
        deriv = models.RecipeDerivations(recipe)
        no_reasons = deriv.can_not_derive_ibu()
        self.assertEquals([], no_reasons)
        ibus = deriv.compute_ibu(decimal.Decimal('1.058'))
        self.assertAlmostEquals(decimal.Decimal('84'), ibus.low, 0)
        self.assertAlmostEquals(decimal.Decimal('118'), ibus.high, 0)
        self.assertAlmostEquals(decimal.Decimal('101'), ibus.average, 0)
        self.assertPercentageSum(ibus.per_hop)

    def testEstimatedOg(self):
        twoRow = models.Grain.objects.get(name__exact='Pale Malt (2-row)')
        grains = [models.RecipeGrain(grain=twoRow, amount_value=decimal.Decimal('10'), amount_units='lb')]
        recipe = Mock(batch_size=5, batch_size_units='gl', efficiency=75, recipegrain_set=FkSet(grains))
        deriv = models.RecipeDerivations(recipe)
        no_reasons = deriv.can_not_derive_og()
        self.assertEquals([], no_reasons)
        og = deriv.compute_og()
        self.assertAlmostEqual(decimal.Decimal('1.0555'), og.low, 3)

    def testEstimatedOgSmuttynoseImperialStout(self):
        '''North American Clonebrews, pp. 87'''
        dec = lambda x: decimal.Decimal(str(x))
        pale = models.Grain.objects.get(name__exact='Pale Malt (2-row)')
        crystal = models.Grain.objects.get(name__exact='Crystal Malt: 90')
        roasted_barley = models.Grain.objects.get(name__exact='Roasted Barley',group__exact='American')
        dark_extract = models.Grain.objects.get(name__exact='Liquid Malt Extract: Dark')
        amber_extract = models.Grain.objects.get(name__exact='Dry Malt Extract: Amber')
        grains = [models.RecipeGrain(grain=pale, amount_value=dec(2), amount_units='lb'),
                  models.RecipeGrain(grain=crystal, amount_value=dec(8), amount_units='oz'),
                  models.RecipeGrain(grain=roasted_barley, amount_value=dec(8), amount_units='oz'),
                  models.RecipeGrain(grain=dark_extract, amount_value=dec(7), amount_units='lb'),
                  models.RecipeGrain(grain=amber_extract, amount_value=dec(1), amount_units='lb')]
        recipe = Mock(batch_size=5, batch_size_units='gl', efficiency=75, recipegrain_set=FkSet(grains))
        deriv = models.RecipeDerivations(recipe)
        no_reasons = deriv.can_not_derive_og()
        self.assertEquals([], no_reasons)
        og = deriv.compute_og()
        self.assertAlmostEquals(dec('1.070'), og.low, 3)
        self.assertPercentageSum(og.per_grain)

    def testEstimatedOgSrmBrains(self):
        '''Clonebrews, pp. 89'''
        dec = lambda x: decimal.Decimal(str(x))
        crystal = models.Grain.objects.get(name__exact='Crystal Malt', group__exact='British')
        light_dme = models.Grain.objects.get(name__exact='Dry Malt Extract: Light')
        cane = models.Grain.objects.get(name__exact='Sucrose (white table sugar)')
        glucose = models.Grain.objects.get(name__exact='Dextrose (glucose)')
        grains = [models.RecipeGrain(grain=crystal, amount_value=dec(0.5), amount_units='lb'),
                  models.RecipeGrain(grain=light_dme, amount_value=dec(4.5), amount_units='lb'),
                  models.RecipeGrain(grain=cane, amount_value=dec(4), amount_units='oz'),
                  models.RecipeGrain(grain=glucose, amount_value=dec(2), amount_units='oz')]
        recipe = Mock(batch_size=5, batch_size_units='gl', efficiency=75, recipegrain_set=FkSet(grains))
        deriv = models.RecipeDerivations(recipe)
        no_reasons = deriv.can_not_derive_og()
        self.assertEquals([], no_reasons)
        og = deriv.compute_og()
        # close … the book's range is 1.041 - 1.043
        self.assertAlmostEquals(dec(1.041), og.low, 3)
        self.assertAlmostEquals(dec(1.043), og.average, 3)
        self.assertAlmostEquals(dec(1.045), og.high, 3)
        #
        no_srm_reasons = deriv.can_not_derive_srm()
        self.assertEquals([], no_srm_reasons)
        srm = deriv.compute_srm()
        # book: 8.5
        # see http://www.homebrewtalk.com/f12/srm-calculations-promash-64792/ for more details.
        # print '\nbrains',srm.low,srm.average,srm.high,'\n'
        self.assertAlmostEquals(dec(8.2), srm.low, 1)
        self.assertAlmostEquals(dec(8.3), srm.average, 1)
        self.assertAlmostEquals(dec(8.5), srm.high, 1)
        self.assertPercentageSum(srm.per_grain)
        #
        self.assertPercentageSum(og.per_grain)

    def testRuabeoir(self):
        '''Brewing Classic Styles, pp. 129; Irish Red Ale "Ruabeoir"'''
        dec = lambda x: decimal.Decimal(str(x))
        pale_lme = models.Grain.objects.get(name__exact='Liquid Malt Extract: Light')
        crystal_40 = models.Grain.objects.get(name__exact='Crystal Malt: 40')
        crystal_120 = models.Grain.objects.get(name__exact='Crystal Malt: 120')
        barley = models.Grain.objects.get(name__exact='Roasted Barley', group__exact='American')
        goldings = models.Hop.objects.get(name__exact='Kent Golding (UK)')
        grains = [models.RecipeGrain(grain=pale_lme, amount_value=dec(8.1), amount_units='lb'),
                  models.RecipeGrain(grain=crystal_40, amount_value=dec(6), amount_units='oz'),
                  models.RecipeGrain(grain=crystal_120, amount_value=dec(6), amount_units='oz'),
                  models.RecipeGrain(grain=barley, amount_value=dec(6), amount_units='oz')]
        hops = [models.RecipeHop(hop=goldings, amount_value=dec(1.25), amount_units='oz', boil_time=60)]
        recipe = Mock(batch_size=5, batch_size_units='gl', efficiency=75,
                      recipegrain_set=FkSet(grains),
                      recipehop_set=FkSet(hops))
        deriv = models.RecipeDerivations(recipe)

        # as the text says:
        # og=1.054
        # ibu=25
        # srm: 17

        no_og_reasons = deriv.can_not_derive_og()
        self.assertEquals([], no_og_reasons)
        og = deriv.compute_og()
        # this is way different from the text:
        # self.assertAlmostEquals(dec('1.062'), og.average, 3)

        no_ibu_reasons = deriv.can_not_derive_ibu()
        self.assertEquals([], no_ibu_reasons)
        ibu = deriv.compute_ibu(og.average)
        # this is way different from the text:
        # self.assertAlmostEquals(dec('25'), ibu.average, 3)

        no_srm_reasons = deriv.can_not_derive_srm()
        self.assertEquals([], no_srm_reasons)
        srm = deriv.compute_srm()
        # this is way different from the text:
        # print 'ruabeoir',srm.low,srm.average,srm.high
        # yself.assertAlmostEquals(dec('17'), srm.average)

    def testEstimatedOgCider(self):
        '''Just basic test of Apple must.'''
        dec = lambda x: decimal.Decimal(str(x))
        apple = models.Grain.objects.get(name__startswith='Apple')
        grains = [models.RecipeGrain(grain=apple, amount_value=dec('5'), amount_units='gl')]
        hops = []
        recipe = Mock(batch_size=5, batch_size_units='gl', efficiency=75,
                      recipegrain_set=FkSet(grains))
        deriv = models.RecipeDerivations(recipe)
        no_og_reasons = deriv.can_not_derive_og()
        self.assertEquals([], no_og_reasons)
        og = deriv.compute_og()
        self.assertAlmostEquals(dec('1.052'), og.average, 3)

    def testEstimatedOgWithOverride(self):
        dec = lambda x: decimal.Decimal(x)
        apple = models.Grain.objects.get(name__startswith='Apple')
        two_row = models.Grain.objects.get(name__exact='Pale Malt (2-row)')
        grains = [models.RecipeGrain(grain=apple, amount_value=dec('5'), amount_units='gl', by_volume_potential_override=dec('1040')),
                  models.RecipeGrain(grain=two_row, amount_value=dec('5'), amount_units='lb', by_weight_potential_override=dec('1016'))]
        hops = []
        recipe = Mock(batch_size=5, batch_size_units='gl', efficiency=75, recipegrain_set=FkSet(grains))
        deriv = models.RecipeDerivations(recipe)
        self.assertEquals([], deriv.can_not_derive_og())
        og = deriv.compute_og()
        self.assertAlmostEquals(dec('1.052'), og.average, 3)

    def testDilutedByVolumePotential(self):
        dec = lambda x: decimal.Decimal(x)
        apple = models.Grain.objects.get(name__startswith='Apple')
        grains = [models.RecipeGrain(grain=apple, amount_value=dec('2.5'), amount_units='gl')]
        hops = []
        recipe = Mock(batch_size=5, batch_size_units='gl', efficiency=75, recipegrain_set=FkSet(grains))
        deriv = models.RecipeDerivations(recipe)
        self.assertEquals([],deriv.can_not_derive_og())
        og = deriv.compute_og()
        self.assertAlmostEquals(dec('1.026'), og.average, 3)

    def testHowToBrewStarterByVolume(self):
        from decimal import Decimal as dec
        '''Pretty common starter ratios, http://www.howtobrew.com/section1/chapter6-5.html'''
        dme = models.Grain.objects.get(name='Dry Malt Extract: Light')
        grains = [models.RecipeGrain(grain=dme, amount_value=dec('0.5'), amount_units='c')]
        recipe = Mock(batch_size=dec('0.5'), batch_size_units='q', efficiency=75, recipegrain_set=FkSet(grains))
        deriv = models.RecipeDerivations(recipe)
        og = deriv.compute_og()
        self.assertAlmostEquals(dec('1.042'), og.average, 3)

    def testTenToOneStarterByWeight(self):
        from decimal import Decimal as dec
        dme = models.Grain.objects.get(name='Dry Malt Extract: Light')
        grains = [models.RecipeGrain(grain=dme, amount_value=dec(80), amount_units='gr')]
        recipe = Mock(batch_size=dec(800), batch_size_units='ml', efficiency=75, recipegrain_set=FkSet(grains))
        deriv = models.RecipeDerivations(recipe)
        og = deriv.compute_og()
        self.assertAlmostEquals(dec('1.035'), og.average, 3)

    def testMeadByWeight(self):
        from decimal import Decimal as dec
        honey = models.Grain.objects.get(name='Honey')
        grains = [models.RecipeGrain(grain=honey, amount_value=dec(1), amount_units='gl')]
        recipe = Mock(batch_size=dec(5), batch_size_units='gl', efficiency=75, recipegrain_set=FkSet(grains))
        deriv = models.RecipeDerivations(recipe)
        og = deriv.compute_og()
        self.assertAlmostEquals(dec('1.106'), og.average, 3);
        

class MashSpargeWaterCalcTest (TestCase):

    def testBrew365Example(self):
        from decimal import Decimal
        calc = models.MashSpargeWaterCalculator()
        calc.grain_size = Decimal('14')
        calc.mash_tun_loss = Decimal('0.5')
        calc.trub_loss = Decimal('1')
        calc.grain_absorption = Decimal('0.15')
        calc.boil_evaporation_rate = Decimal('5')
        calc.mash_thickness = Decimal('1.25')
        #
        calc.grain_temp = Decimal('65')
        calc.target_mash_temp = Decimal('155')

        self.assertAlmostEquals(Decimal('9.18'), calc.total_volume, 2)
        self.assertAlmostEquals(Decimal('4.375'), calc.mash_volume, 2)
        self.assertAlmostEquals(Decimal('4.80'), calc.sparge_volume, 2)
        self.assertAlmostEquals(Decimal('169.4'), calc.strike_temp, 1)


class SeleniumTest (AppTestCase):

    fixtures = ['grains1', 'grains2', 'grains3', 'hops0', 'hops1', 'yeasts1', 'adjuncts', 'yeast-manufacturers', 'yeasts', 'styles']

    def setUp(self):
        from selenium import selenium
        firefox_path = '/usr/lib64/mozilla-firefox/firefox'
        self.selenium = selenium("localhost", 4444, "*firefox %s" % (firefox_path), "http://127.0.0.1:8000/")
        self.selenium.start()

    def tearDown(self):
        # @fixme: only do this on test failure, ideally
        # @fixme: name the captured image something like test case name, when we have more than one
        self.selenium.capture_entire_page_screenshot('/tmp/test.png','')
        self.selenium.stop()

        # pause for a bit to let the operator forcibly kill the test suite,
        # leaving the db intact for interaction
        devel_pause = False
        if devel_pause:
            print 'sleeping'
            import time
            time.sleep(60)

    def click_wait(self, loc, timeout=None):
        if not timeout:
            timeout = 5000
        self.selenium.click(loc)
        self.selenium.wait_for_page_to_load(timeout)

    def _testHappyPath(self):
        sel = self.selenium

        sel.open('/')
        username,password = 'jsled','s3kr1t'
        sel.type('name=username', username)
        sel.type('name=password', password)
        
        self.click_wait('//input[@value="login"]')
        self.assertTrue(sel.is_text_present('invalid username or password'))
        self.assertTrue(username, sel.get_value('name=username'))
        # self.assertTrue(password, selenium.getValue('name=password'))
        
        sel.type('name=password_again', password[:-1])
        self.click_wait('//input[@value="create"]')
        self.assertTrue(sel.is_text_present('Matching passwords required'))
        
        sel.type('name=password_again', password)
        sel.type('name=email', 'josh sled at localhost')
        self.click_wait('//input[@value="create"]')
        self.assertTrue(sel.is_text_present('Must have valid email'))
        
        sel.type('name=email', 'jsled@asynchronous.org')
        self.click_wait('//input[@value="create"]')

        self.assertTrue(sel.get_location().endswith('/user/jsled/profile'))
        self.click_wait('//input[@value="update"]')

        # fixme: factor out something to relate the structure of the input to
        # the other values for the newish ${field()} function. e.g.:
        # self.assertTrue(sel.is_element_present(gen_xpath__errors_for_field('first_name')))
        # self.assertEquals("This field is required", sel.get_text(get_xpath__error_contents_for_field('last_name')))
        self.assertTrue(sel.is_element_present('//input[@name="first_name"]/../../div[@class="errors"]'))
        self.assertTrue(sel.is_element_present('//input[@name="last_name"]/../../div[@class="errors"]'))

        sel.type('name=first_name', 'Josh')
        sel.type('name=last_name', 'Sled')
        self.click_wait('//input[@value="update"]')

        self.assertTrue(sel.get_location().endswith('/user/jsled/'))

        self.click_wait('link=glob:create new recipe*')
        self.assertTrue(sel.get_location().endswith('/recipe/new/'))
        self.click_wait('//input[@value="create"]')

        for field in ('name', 'batch_size'):
            self.assertTrue(sel.is_element_present('//input[@name="%s"]/../ul[@class="errorlist"]/li' % (field)))
        sel.type('name=name', 'Test Recipe Zero')
        sel.type('name=batch_size', '5.025')
        sel.select('name=style', 'label=glob:*(10-A)')
        self.click_wait('//input[@value="create"]')

        self.assertTrue(sel.is_element_present('//input[@name="batch_size"]/../ul[@class="errorlist"]/li'))
        self.assertFalse(sel.is_element_present('//input[@name!="batch_size"]/../ul[@class="errorlist"]/li'))

        sel.type('name=batch_size', '5')
        self.click_wait('//input[@value="create"]')

        self.assertTrue(sel.get_location().endswith('/recipe/1/Test%20Recipe%20Zero'))

        # add more:

        # fail, succeed to add grains
        # edit grains
        # delete grains
        # fail, succeed to add hops
        # edit hops
        # delete hops
        # create brew
        # play with mash/sparge calc
        # create steps
        # adjust step times
        # create more steps

