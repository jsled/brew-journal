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

import datetime
import decimal
import itertools
import re
import unittest

from django.contrib import auth
from django.test.client import Client
from django.test import TestCase
from brewjournal.app import models


class AppTestCase (TestCase):
    fixtures = ['auth', 'grains1', 'grains2', 'grains3', 'hops0', 'hops1', 'yeasts1', 'adjuncts', 'yeast-manufacturers', 'yeasts', 'styles']

    def create_recipe(self, name, date, style, hops, grains):
        res = self.client.post('/recipe/new/', {'name': name, 'insert_date': date, 'batch_size': 5, 'batch_size_units': 'gl', 'style': style, 'type': 'a'})
        self.assertEquals(302, res.status_code, res)
        recipe_url = res['Location']
        recipe_base_url = '/'.join(recipe_url.split('/')[3:-1])
        hop_post_url = '/%s/hop/' % (recipe_base_url)
        for hop,amt,units,boil_time in hops:
            args = {'hop': hop, 'amount_value': amt, 'amount_units': units, 'boil_time': boil_time}
            res = self.client.post(hop_post_url, args)
            self.assertEqual(302, res.status_code, res)
        grain_post_url = '/%s/grain/' % (recipe_base_url)
        for grain,amt,units in grains:
            res = self.client.post(grain_post_url, {'grain': grain, 'amount_value': amt, 'amount_units': units})
            self.assertEqual(302, res.status_code, res)
        return recipe_base_url

    def create_brew(self, user, recipe_id, date, steps):
        brew_res = self.client.post('/user/%s/brew/new/' % (user), {'recipe_id': recipe_id, 'brew_date': date})
        self.assertEquals(302, brew_res.status_code)
        brew_url = '/'.join(brew_res['Location'].split('/')[3:])
        for fields in steps:
            fields.setdefault('brew', -1)
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

        
class NotLoggedInMeansNoActions (TestCase):
    fixtures = ['auth']

    def testUserPage(self):
        res = self.client.get('/user/jsled/')
        # @fixme: what is this character indicative of??
        self.assertNotContains(res, u'»', status_code=200)


class HopWithoutBoilTime (AppTestCase):
    def test(self):
        app = self.client
        app.login(username='jsled', password='s3kr1t')
        res = app.post('/recipe/new/', {'name': 'test', 'insert_date': '2008-08-31 20:48', 'batch_size': 5, 'batch_size_units': 'gl', 'style': 1, 'type': 'a'})
        new_recipe_url = res['Location']
        base_recipe_url = '/'.join(new_recipe_url.split('/')[3:-1])
        hop_post_url = '/%s/hop/' % (base_recipe_url)
        res = app.post(hop_post_url, {'hop': 1, 'amount_value': 2, 'amount_units': 'oz'})
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
                                      [(1, 1, 'oz', 60), (2, 2, 'oz', 30)],
                                      [(1, 1, 'lb'), (2, 2, 'lb')])
        recipe_b = self.create_recipe('test b', '2008-12-26 08:32', 2,
                                      [(1, 1, 'oz', 60), (3, 3, 'oz', 15)],
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
        self.create_brew(user, recipe_a_id, tomorrow, [{'type': 'strike', 'entry_date': str(now), 'date': str(tomorrow)}])
        self.create_brew(user, recipe_b_id, tomorrow, [{'type': 'buy', 'entry_date': str(now), 'date': str(tomorrow)}])
        self.create_brew(user, recipe_c_id, yesterday, [{'type': 'buy', 'entry_date': str(yesterday), 'date': str(now)}])
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
        assertion = re.compile(r'username.{0,20}required', re.IGNORECASE)
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
        res3 = self.client.post(recipe_url, {'name':'test', 'batch_size': '5', 'batch_size_units': 'gl', 'style': 1, 'type': 'a', 'insert_date': new_time_str})
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
        grain_1,grain_2,grain_3 = tuple([models.Grain.objects.get(pk=x) for x in [1,2,3]])
        recipe_url = self.create_recipe('foo', '2009-08-02', 1,
                                        [(hop_1.id, 1, 'oz', 60), (hop_2.id, 2, 'oz', 30)],
                                        [(grain_1.id, 1, 'lb'), (grain_2.id, 2, 'lb'), (grain_3.id, 3, 'ct')])
        res = self.client.get('/' + recipe_url + '/')
        #
        body = res.content.decode('utf-8')
        grain_1_idx = body.find(grain_1.name)
        grain_2_idx = body.find(grain_2.name)
        grain_3_idx = body.find(grain_3.name)
        self.assertTrue(grain_1_idx != -1)
        self.assertTrue(grain_2_idx != -1)
        self.assertTrue(grain_3_idx != -1)
        self.assertTrue(grain_2_idx < grain_1_idx)
        self.assertTrue(grain_3_idx > grain_1_idx)
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

    fixtures = ['hops0', 'grains1']

    def assertPercentageSum(self, thingies):
        percentage_accum = decimal.Decimal('0')
        for thingy in thingies:
            percentage_accum += thingy.percentage
        self.assertAlmostEquals(decimal.Decimal('100'), percentage_accum, 0)

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
        # this is straight from http://www.howtobrew.com/section1/chapter5-5.html
        perle = Mock(aau_low=decimal.Decimal('6.4'), aau_high=decimal.Decimal('6.4'))
        liberty = Mock(aau_low=decimal.Decimal('4.6'), aau_high=decimal.Decimal('4.6'))
        hops = [Mock(boil_time=60, amount_value=decimal.Decimal('1.5'), amount_units='oz', hop=perle),
                Mock(boil_time=15, amount_value=decimal.Decimal('1'), amount_units='oz', hop=liberty)]
        recipe = Mock(batch_size=5, batch_size_units='gl', recipehop_set=FkSet(hops))
        deriv = models.RecipeDerivations(recipe)
        no_reasons = deriv.can_not_derive_ibu()
        self.assertEquals([], no_reasons)
        ibus = deriv.compute_ibu(decimal.Decimal('1.080'))
        self.assertAlmostEquals(decimal.Decimal('32'), ibus.average, 0)

    def testRealWorldIbus(self):
        chinook = models.Hop.objects.get(name__exact='Chinook')
        golding = models.Hop.objects.get(name__exact='Golding (US)')
        hops = [Mock(boil_time=90, amount_value=decimal.Decimal('2'), amount_units='oz', hop=chinook),
                Mock(boil_time=90, amount_value=decimal.Decimal('1'), amount_units='oz', hop=golding)]
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
        grains = [Mock(grain=twoRow, amount_value=decimal.Decimal('10'), amount_units='lb')]
        recipe = Mock(batch_size=5, batch_size_units='gl', recipegrain_set=FkSet(grains))
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
        grains = [Mock(grain=pale, amount_value=dec(2), amount_units='lb'),
                  Mock(grain=crystal, amount_value=dec(8), amount_units='oz'),
                  Mock(grain=roasted_barley, amount_value=dec(8), amount_units='oz'),
                  Mock(grain=dark_extract, amount_value=dec(7), amount_units='lb'),
                  Mock(grain=amber_extract, amount_value=dec(1), amount_units='lb')]
        recipe = Mock(batch_size=5, batch_size_units='gl', recipegrain_set=FkSet(grains))
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
        grains = [Mock(grain=crystal, amount_value=dec(0.5), amount_units='lb'),
                  Mock(grain=light_dme, amount_value=dec(4.5), amount_units='lb'),
                  Mock(grain=cane, amount_value=dec(4), amount_units='oz'),
                  Mock(grain=glucose, amount_value=dec(2), amount_units='oz')]
        recipe = Mock(batch_size=5, batch_size_units='gl', recipegrain_set=FkSet(grains))
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
        grains = [Mock(grain=pale_lme, amount_value=dec(8.1), amount_units='lb'),
                  Mock(grain=crystal_40, amount_value=dec(6), amount_units='oz'),
                  Mock(grain=crystal_120, amount_value=dec(6), amount_units='oz'),
                  Mock(grain=barley, amount_value=dec(6), amount_units='oz')]
        hops = [Mock(hop=goldings, amount_value=dec(1.25), amount_units='oz', boil_time=60)]
        recipe = Mock(batch_size=5, batch_size_units='gl',
                      recipegrain_set=FkSet(grains),
                      recipehop_set=FkSet(hops))
        deriv = models.RecipeDerivations(recipe)
        no_og_reasons = deriv.can_not_derive_og()
        self.assertEquals([], no_og_reasons)
        og = deriv.compute_og()
        self.assertAlmostEquals(dec('1.054'), og.average, 0)

        # as the text says:
        # og=1.054
        # ibu=25
        # srm: 17

        no_ibu_reasons = deriv.can_not_derive_ibu()
        self.assertEquals([], no_ibu_reasons)
        ibu = deriv.compute_ibu(og.average)
        # this is way different from the text:
        # self.assertAlmostEquals(dec('25'), ibu.average, 0)

        no_srm_reasons = deriv.can_not_derive_srm()
        self.assertEquals([], no_srm_reasons)
        srm = deriv.compute_srm()
        # this is way different from the text:
        # print 'ruabeoir',srm.low,srm.average,srm.high
        # yself.assertAlmostEquals(dec('17'), srm.average)
