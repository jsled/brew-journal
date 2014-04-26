# Copyright (c) 2008-2010, Joshua Sled <jsled@asynchronous.org>
# See LICENSE file for "New BSD" license details.

from django.contrib import admin

from app import models

for cls in (models.Style,
            models.Grain,
            models.Hop,
            models.Adjunct,
            models.YeastManufacturer,
            models.Yeast,
            models.Recipe,
            models.RecipeGrain,
            models.RecipeHop,
            models.RecipeYeast,
            models.RecipeAdjunct,
            models.Brew,
            models.Step,
            models.UserProfile):
    admin.site.register(cls)
