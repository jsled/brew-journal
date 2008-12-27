# -*- encoding: utf-8 -*-
import decimal
import unittest
from django.test.client import Client
from django.test import TestCase
import util
from brewjournal.app import models


class AppTestCase (TestCase):
    fixtures = ['auth', 'grains1', 'grains2', 'grains3', 'hops0', 'hops1', 'yeasts1', 'adjuncts', 'yeast-manufacturers', 'yeasts', 'styles']

    def create_recipe(self, name, date, style, hops, grains):
        res = self.client.post('/recipe/new/', {'name': name, 'insert_date': date, 'batch_size': 5, 'batch_size_units': 'gl', 'style': style, 'type': 'a'})
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
            self.assertContains(res, u'test a')
            self.assertContains(res, u'test b')
            self.assertNotContains(res, u'test c', 200)
            self.assertContains(res, u'1 oz', count=2)
            self.assertContains(res, u'2 oz', count=1)
            self.assertContains(res, u'3 oz', count=1)
            self.assertContains(res, u'1 lb', count=2)
            self.assertContains(res, u'2 lb', count=1)
            self.assertContains(res, u'3 lb', count=1)
            self.assertNotContains(res, u'20 oz', 200)
            self.assertNotContains(res, u'20 lb', 200)
            # @fixme: more appropriate assertions
        except Exception,e:
            print res
            raise e
                          


# - creating a new user
#   - invalid user name
# - creating a recipe
#   - adding items to a recipe
#   - changing a recipe
# - creating a brew from a recipe
#   - adding steps to the brew

class MockStep (object):
    def __init__(self, type, gravity):
        self._type = type
        self._gravity = decimal.Decimal(gravity)
    type = property(lambda s: s._type)
    gravity = property(lambda s: s._gravity)


class MockSteppedBrew (object):
    def __init__(self, **kwargs):
        self._steps = kwargs.get('steps', [])
        pass

    step_set = property(lambda s: s._get_step_set())
    steps = property(lambda s: s._steps)

    def _get_step_set(self):
        class _StepSet (object):
            def __init__(self, brew):
                self._brew = brew
                
            def all(self):
                return self._brew.steps

        return _StepSet(self)


class BrewDerivativesTest (TestCase):
    def testNoAbvComputation(self):
        brew = models.Brew()
        derivs = util.BrewDerivations(brew)
        cannot = derivs.can_not_derive_abv()
        self.assertTrue(len(cannot) > 0, len(cannot))
        self.assertEquals(2, len(cannot))

    def testMultiStepAbvComputation(self):
        brew = MockSteppedBrew(steps=[MockStep('boil-start', '1.049'),
                                      MockStep('pitch', '1.064'),
                                      MockStep('keg', '1.022')])
        derivs = util.BrewDerivations(brew)
        abv = derivs.alcohol_by_volume()
        self.assert_(abv > decimal.Decimal('3.645'), str(abv))
        self.assertEquals(abv, decimal.Decimal('5.67'), str(abv))

    def testNoEfficiencyComputations(self):
        brew = models.Brew(recipe=models.Recipe())
        derivs = util.BrewDerivations(brew)
        cannot = derivs.can_not_derive_efficiency()
        self.assertTrue(len(cannot) > 0, len(cannot))
        self.assertEquals(2, len(cannot))

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

    # testDisabledAccount


class TestReg (AppTestCase):
    fixtures = ['auth']

    def testBrokenReg(self):
        res = self.client.post('/', {'sub': 'create', 'username': 'bill', 'password': 'foo', 'password_again': 'bar', 'email': 'invalid'})
        self.assertContains(res, 'Passwords must match', status_code=200)
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

    # testUnknownSubmitType


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
        groceries = models.ShoppingList([b1, b2, b3])
        self.assertEquals(10, len(groceries.grains))
        self.assertEquals(10, len(groceries.hops))
        for grain,brews in groceries.grains:
            self.assertTrue(len(brews) <= 3)
        for hop,brews in groceries.hops:
            self.assertTrue(len(brews) <= 3)
