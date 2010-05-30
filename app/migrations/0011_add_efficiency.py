# -*- encoding: utf-8 -*-

from south.db import db
from django.db import models
from brewjournal.app.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'UserProfile.pref_brewhouse_efficiency'
        db.add_column('app_userprofile', 'pref_brewhouse_efficiency', orm['app.userprofile:pref_brewhouse_efficiency'])
        
        # Adding field 'Recipe.efficiency'
        db.add_column('app_recipe', 'efficiency', orm['app.recipe:efficiency'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'UserProfile.pref_brewhouse_efficiency'
        db.delete_column('app_userprofile', 'pref_brewhouse_efficiency')
        
        # Deleting field 'Recipe.efficiency'
        db.delete_column('app_recipe', 'efficiency')
        
    
    
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'volume_potential_max': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'volume_potential_min': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'volume_to_weight_conversion': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '3'})
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
            'boil_length': ('django.db.models.fields.DecimalField', [], {'default': '60', 'max_digits': '3', 'decimal_places': '0'}),
            'derived_from_recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']", 'null': 'True', 'blank': 'True'}),
            'efficiency': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': "'75'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pre_boil_volume': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'pre_boil_volume_units': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'style': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Style']", 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '1'})
        },
        'app.recipeadjunct': {
            'adjunct': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Adjunct']"}),
            'amount_units': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'amount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '3'}),
            'boil_time': ('django.db.models.fields.SmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"})
        },
        'app.recipegrain': {
            'amount_units': ('django.db.models.fields.CharField', [], {'default': "'lb'", 'max_length': '4'}),
            'amount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '3'}),
            'by_volume_potential_override': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'by_weight_potential_override': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'grain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Grain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"})
        },
        'app.recipehop': {
            'aau_override': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1', 'blank': 'True'}),
            'amount_units': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'amount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'boil_time': ('django.db.models.fields.SmallIntegerField', [], {}),
            'hop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Hop']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"}),
            'usage_type': ('django.db.models.fields.CharField', [], {'default': "'boil'", 'max_length': '4'})
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
            'gravity_read_type': ('django.db.models.fields.CharField', [], {'default': "'sg'", 'max_length': '3'}),
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
            'pref_brewhouse_efficiency': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': "'75'"}),
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
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
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
