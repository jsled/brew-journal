# -*- encoding: utf-8 -*-

from south.db import db
from django.db import models
from app.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Yeast'
        db.create_table('app_yeast', (
            ('id', orm['app.Yeast:id']),
            ('manufacturer', orm['app.Yeast:manufacturer']),
            ('ident', orm['app.Yeast:ident']),
            ('name', orm['app.Yeast:name']),
            ('description', orm['app.Yeast:description']),
            ('type', orm['app.Yeast:type']),
        ))
        db.send_create_signal('app', ['Yeast'])
        
        # Adding model 'RecipeYeast'
        db.create_table('app_recipeyeast', (
            ('id', orm['app.RecipeYeast:id']),
            ('recipe', orm['app.RecipeYeast:recipe']),
            ('yeast', orm['app.RecipeYeast:yeast']),
            ('ideal', orm['app.RecipeYeast:ideal']),
        ))
        db.send_create_signal('app', ['RecipeYeast'])
        
        # Adding model 'YeastManufacturer'
        db.create_table('app_yeastmanufacturer', (
            ('id', orm['app.YeastManufacturer:id']),
            ('name', orm['app.YeastManufacturer:name']),
        ))
        db.send_create_signal('app', ['YeastManufacturer'])
        
        # Adding model 'Brew'
        db.create_table('app_brew', (
            ('id', orm['app.Brew:id']),
            ('brew_date', orm['app.Brew:brew_date']),
            ('brewer', orm['app.Brew:brewer']),
            ('notes', orm['app.Brew:notes']),
            ('recipe', orm['app.Brew:recipe']),
            ('last_update_date', orm['app.Brew:last_update_date']),
            ('last_state', orm['app.Brew:last_state']),
            ('is_done', orm['app.Brew:is_done']),
        ))
        db.send_create_signal('app', ['Brew'])
        
        # Adding model 'Style'
        db.create_table('app_style', (
            ('id', orm['app.Style:id']),
            ('name', orm['app.Style:name']),
            ('bjcp_code', orm['app.Style:bjcp_code']),
            ('parent', orm['app.Style:parent']),
        ))
        db.send_create_signal('app', ['Style'])
        
        # Adding model 'RecipeGrain'
        db.create_table('app_recipegrain', (
            ('id', orm['app.RecipeGrain:id']),
            ('recipe', orm['app.RecipeGrain:recipe']),
            ('grain', orm['app.RecipeGrain:grain']),
            ('amount_value', orm['app.RecipeGrain:amount_value']),
            ('amount_units', orm['app.RecipeGrain:amount_units']),
        ))
        db.send_create_signal('app', ['RecipeGrain'])
        
        # Adding model 'Grain'
        db.create_table('app_grain', (
            ('id', orm['app.Grain:id']),
            ('name', orm['app.Grain:name']),
            ('extract_min', orm['app.Grain:extract_min']),
            ('extract_max', orm['app.Grain:extract_max']),
            ('lovibond_min', orm['app.Grain:lovibond_min']),
            ('lovibond_max', orm['app.Grain:lovibond_max']),
            ('description', orm['app.Grain:description']),
            ('group', orm['app.Grain:group']),
        ))
        db.send_create_signal('app', ['Grain'])
        
        # Adding model 'Recipe'
        db.create_table('app_recipe', (
            ('id', orm['app.Recipe:id']),
            ('author', orm['app.Recipe:author']),
            ('name', orm['app.Recipe:name']),
            ('insert_date', orm['app.Recipe:insert_date']),
            ('batch_size', orm['app.Recipe:batch_size']),
            ('batch_size_units', orm['app.Recipe:batch_size_units']),
            ('style', orm['app.Recipe:style']),
            ('derived_from_recipe', orm['app.Recipe:derived_from_recipe']),
            ('type', orm['app.Recipe:type']),
            ('source_url', orm['app.Recipe:source_url']),
            ('notes', orm['app.Recipe:notes']),
        ))
        db.send_create_signal('app', ['Recipe'])
        
        # Adding model 'StarredRecipe'
        db.create_table('app_starredrecipe', (
            ('id', orm['app.StarredRecipe:id']),
            ('recipe', orm['app.StarredRecipe:recipe']),
            ('user', orm['app.StarredRecipe:user']),
            ('when', orm['app.StarredRecipe:when']),
            ('notes', orm['app.StarredRecipe:notes']),
        ))
        db.send_create_signal('app', ['StarredRecipe'])
        
        # Adding model 'Hop'
        db.create_table('app_hop', (
            ('id', orm['app.Hop:id']),
            ('name', orm['app.Hop:name']),
            ('aau_low', orm['app.Hop:aau_low']),
            ('aau_high', orm['app.Hop:aau_high']),
        ))
        db.send_create_signal('app', ['Hop'])
        
        # Adding model 'RecipeHop'
        db.create_table('app_recipehop', (
            ('id', orm['app.RecipeHop:id']),
            ('recipe', orm['app.RecipeHop:recipe']),
            ('hop', orm['app.RecipeHop:hop']),
            ('amount_value', orm['app.RecipeHop:amount_value']),
            ('amount_units', orm['app.RecipeHop:amount_units']),
            ('boil_time', orm['app.RecipeHop:boil_time']),
        ))
        db.send_create_signal('app', ['RecipeHop'])
        
        # Adding model 'Step'
        db.create_table('app_step', (
            ('id', orm['app.Step:id']),
            ('brew', orm['app.Step:brew']),
            ('type', orm['app.Step:type']),
            ('date', orm['app.Step:date']),
            ('entry_date', orm['app.Step:entry_date']),
            ('volume', orm['app.Step:volume']),
            ('volume_units', orm['app.Step:volume_units']),
            ('temp', orm['app.Step:temp']),
            ('temp_units', orm['app.Step:temp_units']),
            ('gravity_read', orm['app.Step:gravity_read']),
            ('gravity_read_temp', orm['app.Step:gravity_read_temp']),
            ('gravity_read_temp_units', orm['app.Step:gravity_read_temp_units']),
            ('notes', orm['app.Step:notes']),
        ))
        db.send_create_signal('app', ['Step'])
        
        # Adding model 'RecipeAdjunct'
        db.create_table('app_recipeadjunct', (
            ('id', orm['app.RecipeAdjunct:id']),
            ('recipe', orm['app.RecipeAdjunct:recipe']),
            ('adjunct', orm['app.RecipeAdjunct:adjunct']),
            ('amount_value', orm['app.RecipeAdjunct:amount_value']),
            ('amount_units', orm['app.RecipeAdjunct:amount_units']),
            ('boil_time', orm['app.RecipeAdjunct:boil_time']),
            ('notes', orm['app.RecipeAdjunct:notes']),
        ))
        db.send_create_signal('app', ['RecipeAdjunct'])
        
        # Adding model 'UserProfile'
        db.create_table('app_userprofile', (
            ('id', orm['app.UserProfile:id']),
            ('user', orm['app.UserProfile:user']),
            ('pref_brew_type', orm['app.UserProfile:pref_brew_type']),
            ('pref_make_starter', orm['app.UserProfile:pref_make_starter']),
            ('pref_secondary_ferm', orm['app.UserProfile:pref_secondary_ferm']),
            ('pref_dispensing_style', orm['app.UserProfile:pref_dispensing_style']),
            ('timezone', orm['app.UserProfile:timezone']),
        ))
        db.send_create_signal('app', ['UserProfile'])
        
        # Adding model 'Adjunct'
        db.create_table('app_adjunct', (
            ('id', orm['app.Adjunct:id']),
            ('name', orm['app.Adjunct:name']),
            ('group', orm['app.Adjunct:group']),
        ))
        db.send_create_signal('app', ['Adjunct'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Yeast'
        db.delete_table('app_yeast')
        
        # Deleting model 'RecipeYeast'
        db.delete_table('app_recipeyeast')
        
        # Deleting model 'YeastManufacturer'
        db.delete_table('app_yeastmanufacturer')
        
        # Deleting model 'Brew'
        db.delete_table('app_brew')
        
        # Deleting model 'Style'
        db.delete_table('app_style')
        
        # Deleting model 'RecipeGrain'
        db.delete_table('app_recipegrain')
        
        # Deleting model 'Grain'
        db.delete_table('app_grain')
        
        # Deleting model 'Recipe'
        db.delete_table('app_recipe')
        
        # Deleting model 'StarredRecipe'
        db.delete_table('app_starredrecipe')
        
        # Deleting model 'Hop'
        db.delete_table('app_hop')
        
        # Deleting model 'RecipeHop'
        db.delete_table('app_recipehop')
        
        # Deleting model 'Step'
        db.delete_table('app_step')
        
        # Deleting model 'RecipeAdjunct'
        db.delete_table('app_recipeadjunct')
        
        # Deleting model 'UserProfile'
        db.delete_table('app_userprofile')
        
        # Deleting model 'Adjunct'
        db.delete_table('app_adjunct')
        
    
    
    models = {
        'app.adjunct': {
            'group': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'app.brew': {
            'brew_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'brewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_done': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'last_update_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']", 'null': 'True'})
        },
        'app.grain': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'extract_max': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'extract_min': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lovibond_max': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'lovibond_min': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'app.hop': {
            'aau_high': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '1'}),
            'aau_low': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'app.recipe': {
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'batch_size': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'batch_size_units': ('django.db.models.fields.CharField', [], {'default': "'gl'", 'max_length': '4'}),
            'derived_from_recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'style': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Style']", 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '1'})
        },
        'app.recipeadjunct': {
            'adjunct': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Adjunct']"}),
            'amount_units': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'amount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'boil_time': ('django.db.models.fields.SmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"})
        },
        'app.recipegrain': {
            'amount_units': ('django.db.models.fields.CharField', [], {'default': "'lb'", 'max_length': '2'}),
            'amount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'grain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Grain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"})
        },
        'app.recipehop': {
            'amount_units': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'amount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'boil_time': ('django.db.models.fields.SmallIntegerField', [], {}),
            'hop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Hop']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"})
        },
        'app.recipeyeast': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ideal': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"}),
            'yeast': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Yeast']"})
        },
        'app.starredrecipe': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'app.step': {
            'brew': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Brew']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'entry_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'gravity_read': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3', 'blank': 'True'}),
            'gravity_read_temp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'gravity_read_temp_units': ('django.db.models.fields.CharField', [], {'default': "'f'", 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'temp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'temp_units': ('django.db.models.fields.CharField', [], {'default': "'f'", 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'volume': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'volume_units': ('django.db.models.fields.CharField', [], {'default': "'gl'", 'max_length': '4', 'null': 'True', 'blank': 'True'})
        },
        'app.style': {
            'bjcp_code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Style']", 'null': 'True'})
        },
        'app.userprofile': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pref_brew_type': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '1'}),
            'pref_dispensing_style': ('django.db.models.fields.CharField', [], {'default': "'b'", 'max_length': '1'}),
            'pref_make_starter': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'pref_secondary_ferm': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'timezone': ('TimeZoneField', [], {'default': "'UTC'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'app.yeast': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.YeastManufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '7'})
        },
        'app.yeastmanufacturer': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['app']
