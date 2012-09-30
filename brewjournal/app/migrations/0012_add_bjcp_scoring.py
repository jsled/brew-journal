# -*- encoding: utf-8 -*-

from south.db import db
from django.db import models
from brewjournal.app.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'BjcpCompetitionResults'
        db.create_table('app_bjcpcompetitionresults', (
            ('id', orm['app.bjcpcompetitionresults:id']),
            ('brew', orm['app.bjcpcompetitionresults:brew']),
            ('entry_id', orm['app.bjcpcompetitionresults:entry_id']),
            ('entered_style', orm['app.bjcpcompetitionresults:entered_style']),
            ('competition_name', orm['app.bjcpcompetitionresults:competition_name']),
            ('competition_date', orm['app.bjcpcompetitionresults:competition_date']),
            ('competition_url', orm['app.bjcpcompetitionresults:competition_url']),
            ('entry_number', orm['app.bjcpcompetitionresults:entry_number']),
            ('flight_position', orm['app.bjcpcompetitionresults:flight_position']),
            ('flight_entries', orm['app.bjcpcompetitionresults:flight_entries']),
            ('assigned_score', orm['app.bjcpcompetitionresults:assigned_score']),
            ('place_awarded', orm['app.bjcpcompetitionresults:place_awarded']),
            ('mini_bos', orm['app.bjcpcompetitionresults:mini_bos']),
            ('notes', orm['app.bjcpcompetitionresults:notes']),
        ))
        db.send_create_signal('app', ['BjcpCompetitionResults'])
        
        # Adding model 'BjcpBeerScoresheet'
        db.create_table('app_bjcpbeerscoresheet', (
            ('id', orm['app.bjcpbeerscoresheet:id']),
            ('competition_results', orm['app.bjcpbeerscoresheet:competition_results']),
            ('judge_name', orm['app.bjcpbeerscoresheet:judge_name']),
            ('judge_bjcp_id', orm['app.bjcpbeerscoresheet:judge_bjcp_id']),
            ('judge_email', orm['app.bjcpbeerscoresheet:judge_email']),
            ('judge_rank', orm['app.bjcpbeerscoresheet:judge_rank']),
            ('bottle_inspection', orm['app.bjcpbeerscoresheet:bottle_inspection']),
            ('bottle_inspection_notes', orm['app.bjcpbeerscoresheet:bottle_inspection_notes']),
            ('notes', orm['app.bjcpbeerscoresheet:notes']),
            ('total_score', orm['app.bjcpbeerscoresheet:total_score']),
            ('aroma_score', orm['app.bjcpbeerscoresheet:aroma_score']),
            ('aroma_notes', orm['app.bjcpbeerscoresheet:aroma_notes']),
            ('appearance_score', orm['app.bjcpbeerscoresheet:appearance_score']),
            ('appearance_notes', orm['app.bjcpbeerscoresheet:appearance_notes']),
            ('flavor_score', orm['app.bjcpbeerscoresheet:flavor_score']),
            ('flavor_notes', orm['app.bjcpbeerscoresheet:flavor_notes']),
            ('mouthfeel_score', orm['app.bjcpbeerscoresheet:mouthfeel_score']),
            ('mouthfeel_notes', orm['app.bjcpbeerscoresheet:mouthfeel_notes']),
            ('overall_score', orm['app.bjcpbeerscoresheet:overall_score']),
            ('overall_notes', orm['app.bjcpbeerscoresheet:overall_notes']),
            ('stylistic_accuracy', orm['app.bjcpbeerscoresheet:stylistic_accuracy']),
            ('technical_merit', orm['app.bjcpbeerscoresheet:technical_merit']),
            ('intangibles', orm['app.bjcpbeerscoresheet:intangibles']),
        ))
        db.send_create_signal('app', ['BjcpBeerScoresheet'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'BjcpCompetitionResults'
        db.delete_table('app_bjcpcompetitionresults')
        
        # Deleting model 'BjcpBeerScoresheet'
        db.delete_table('app_bjcpbeerscoresheet')
        
    
    
    models = {
        'app.adjunct': {
            'group': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'app.bjcpbeerscoresheet': {
            'appearance_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'appearance_score': ('django.db.models.fields.IntegerField', [], {}),
            'aroma_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'aroma_score': ('django.db.models.fields.IntegerField', [], {}),
            'bottle_inspection': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'bottle_inspection_notes': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'competition_results': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.BjcpCompetitionResults']"}),
            'flavor_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'flavor_score': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intangibles': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'judge_bjcp_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'judge_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'judge_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'judge_rank': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'mouthfeel_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mouthfeel_score': ('django.db.models.fields.IntegerField', [], {}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'overall_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'overall_score': ('django.db.models.fields.IntegerField', [], {}),
            'stylistic_accuracy': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'technical_merit': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'total_score': ('django.db.models.fields.IntegerField', [], {})
        },
        'app.bjcpcompetitionresults': {
            'assigned_score': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '1'}),
            'brew': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Brew']"}),
            'competition_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'competition_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'competition_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'entered_style': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Style']"}),
            'entry_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'entry_number': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'flight_entries': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flight_position': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mini_bos': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'place_awarded': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'})
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
