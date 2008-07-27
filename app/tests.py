# -*- encoding: utf-8 -*-
import unittest
from django.test.client import Client
from django.test import TestCase

class BasicLoginTest (TestCase):
    fixtures = ['auth', 'grains1', 'grains2', 'hops', 'yeast-manufacturers', 'yeasts', 'styles']

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
