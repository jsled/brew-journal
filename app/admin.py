from django.contrib import admin

from brewjournal.app import models

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
            models.StarredRecipe,
            models.Brew,
            models.Step):
    admin.site.register(cls)
