# -*- encoding: utf-8 -*-
import unittest
from django.test.client import Client
from django.test import TestCase

class AppTestCase (TestCase):
    fixtures = ['auth', 'grains1', 'grains2', 'grains3', 'hops', 'hops1', 'yeasts1', 'adjuncts', 'yeast-manufacturers', 'yeasts', 'styles']


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
        # self.assertNotContains(res, u'»', 200)
        self.assert_(res.content.find('»') == -1)


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
        self.assertEqual(302, res.status_code)

# - creating a new user
#   - invalid user name
# - creating a recipe
#   - adding items to a recipe
#   - changing a recipe
# - creating a brew from a recipe
#   - adding steps to the brew
