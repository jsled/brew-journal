# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SourcedHopDetails'
        db.create_table('app_sourcedhopdetails', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=6, null=True)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True)),
            ('alpha_acid_low', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('alpha_acid_high', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('beta_acid_low', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('beta_acid_high', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('cohumulone_pctg_low', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('cohumulone_pctg_high', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('oils_low', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('oils_high', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('myrcene_pctg_low', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('myrcene_pctg_high', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('humulene_pctg_low', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('humulene_pctg_high', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('caryophyllene_pctg_low', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('caryophyllene_pctg_high', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('farnesene_pctg_low', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('farnesene_pctg_high', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('storage_low', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('storage_high', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1)),
            ('storage_label', self.gf('django.db.models.fields.TextField')(null=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('app', ['SourcedHopDetails'])

        # Adding field 'Hop.region'
        db.add_column('app_hop', 'region',
                      self.gf('django.db.models.fields.CharField')(default='us', max_length=2),
                      keep_default=False)

        # Adding field 'Hop.type'
        db.add_column('app_hop', 'type',
                      self.gf('django.db.models.fields.CharField')(max_length=6, null=True),
                      keep_default=False)

        # Adding field 'Hop.desc'
        db.add_column('app_hop', 'desc',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)

        # Adding field 'Hop.alpha_acid_low'
        db.add_column('app_hop', 'alpha_acid_low',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.alpha_acid_high'
        db.add_column('app_hop', 'alpha_acid_high',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.beta_acid_low'
        db.add_column('app_hop', 'beta_acid_low',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.beta_acid_high'
        db.add_column('app_hop', 'beta_acid_high',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.cohumulone_pctg_low'
        db.add_column('app_hop', 'cohumulone_pctg_low',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.cohumulone_pctg_high'
        db.add_column('app_hop', 'cohumulone_pctg_high',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.oils_low'
        db.add_column('app_hop', 'oils_low',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.oils_high'
        db.add_column('app_hop', 'oils_high',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.myrcene_pctg_low'
        db.add_column('app_hop', 'myrcene_pctg_low',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.myrcene_pctg_high'
        db.add_column('app_hop', 'myrcene_pctg_high',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.humulene_pctg_low'
        db.add_column('app_hop', 'humulene_pctg_low',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.humulene_pctg_high'
        db.add_column('app_hop', 'humulene_pctg_high',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.caryophyllene_pctg_low'
        db.add_column('app_hop', 'caryophyllene_pctg_low',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.caryophyllene_pctg_high'
        db.add_column('app_hop', 'caryophyllene_pctg_high',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.farnesene_pctg_low'
        db.add_column('app_hop', 'farnesene_pctg_low',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.farnesene_pctg_high'
        db.add_column('app_hop', 'farnesene_pctg_high',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.storage_low'
        db.add_column('app_hop', 'storage_low',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.storage_high'
        db.add_column('app_hop', 'storage_high',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1),
                      keep_default=False)

        # Adding field 'Hop.storage_label'
        db.add_column('app_hop', 'storage_label',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)

        # Adding field 'Hop.notes'
        db.add_column('app_hop', 'notes',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)


        # Changing field 'UserProfile.timezone'
        db.alter_column('app_userprofile', 'timezone', self.gf('timezones.fields.TimeZoneField')())

    def backwards(self, orm):
        # Deleting model 'SourcedHopDetails'
        db.delete_table('app_sourcedhopdetails')

        # Deleting field 'Hop.region'
        db.delete_column('app_hop', 'region')

        # Deleting field 'Hop.type'
        db.delete_column('app_hop', 'type')

        # Deleting field 'Hop.desc'
        db.delete_column('app_hop', 'desc')

        # Deleting field 'Hop.alpha_acid_low'
        db.delete_column('app_hop', 'alpha_acid_low')

        # Deleting field 'Hop.alpha_acid_high'
        db.delete_column('app_hop', 'alpha_acid_high')

        # Deleting field 'Hop.beta_acid_low'
        db.delete_column('app_hop', 'beta_acid_low')

        # Deleting field 'Hop.beta_acid_high'
        db.delete_column('app_hop', 'beta_acid_high')

        # Deleting field 'Hop.cohumulone_pctg_low'
        db.delete_column('app_hop', 'cohumulone_pctg_low')

        # Deleting field 'Hop.cohumulone_pctg_high'
        db.delete_column('app_hop', 'cohumulone_pctg_high')

        # Deleting field 'Hop.oils_low'
        db.delete_column('app_hop', 'oils_low')

        # Deleting field 'Hop.oils_high'
        db.delete_column('app_hop', 'oils_high')

        # Deleting field 'Hop.myrcene_pctg_low'
        db.delete_column('app_hop', 'myrcene_pctg_low')

        # Deleting field 'Hop.myrcene_pctg_high'
        db.delete_column('app_hop', 'myrcene_pctg_high')

        # Deleting field 'Hop.humulene_pctg_low'
        db.delete_column('app_hop', 'humulene_pctg_low')

        # Deleting field 'Hop.humulene_pctg_high'
        db.delete_column('app_hop', 'humulene_pctg_high')

        # Deleting field 'Hop.caryophyllene_pctg_low'
        db.delete_column('app_hop', 'caryophyllene_pctg_low')

        # Deleting field 'Hop.caryophyllene_pctg_high'
        db.delete_column('app_hop', 'caryophyllene_pctg_high')

        # Deleting field 'Hop.farnesene_pctg_low'
        db.delete_column('app_hop', 'farnesene_pctg_low')

        # Deleting field 'Hop.farnesene_pctg_high'
        db.delete_column('app_hop', 'farnesene_pctg_high')

        # Deleting field 'Hop.storage_low'
        db.delete_column('app_hop', 'storage_low')

        # Deleting field 'Hop.storage_high'
        db.delete_column('app_hop', 'storage_high')

        # Deleting field 'Hop.storage_label'
        db.delete_column('app_hop', 'storage_label')

        # Deleting field 'Hop.notes'
        db.delete_column('app_hop', 'notes')


        # Changing field 'UserProfile.timezone'
        db.alter_column('app_userprofile', 'timezone', self.gf('TimeZoneField')())

    models = {
        'app.adjunct': {
            'Meta': {'object_name': 'Adjunct'},
            'group': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'app.bjcpbeerscoresheet': {
            'Meta': {'object_name': 'BjcpBeerScoresheet'},
            'appearance_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'appearance_score': ('django.db.models.fields.IntegerField', [], {}),
            'aroma_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'aroma_score': ('django.db.models.fields.IntegerField', [], {}),
            'bottle_inspection': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'Meta': {'object_name': 'BjcpCompetitionResults'},
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
            'Meta': {'ordering': "['brew_date', 'last_update_date']", 'object_name': 'Brew'},
            'brew_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'brewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'last_update_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']", 'null': 'True'})
        },
        'app.grain': {
            'Meta': {'object_name': 'Grain'},
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
            'Meta': {'object_name': 'Hop'},
            'aau_high': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '1'}),
            'aau_low': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '1'}),
            'alpha_acid_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'alpha_acid_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'beta_acid_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'beta_acid_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'caryophyllene_pctg_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'caryophyllene_pctg_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'cohumulone_pctg_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'cohumulone_pctg_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'farnesene_pctg_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'farnesene_pctg_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'humulene_pctg_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'humulene_pctg_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'myrcene_pctg_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'myrcene_pctg_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'oils_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'oils_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'region': ('django.db.models.fields.CharField', [], {'default': "'us'", 'max_length': '2'}),
            'storage_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'storage_label': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'storage_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True'})
        },
        'app.recipe': {
            'Meta': {'object_name': 'Recipe'},
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
            'Meta': {'object_name': 'RecipeAdjunct'},
            'adjunct': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Adjunct']"}),
            'amount_units': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'amount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '3'}),
            'boil_time': ('django.db.models.fields.SmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"})
        },
        'app.recipegrain': {
            'Meta': {'object_name': 'RecipeGrain'},
            'amount_units': ('django.db.models.fields.CharField', [], {'default': "'lb'", 'max_length': '4'}),
            'amount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '3'}),
            'by_volume_potential_override': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'by_weight_potential_override': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'grain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Grain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"})
        },
        'app.recipehop': {
            'Meta': {'object_name': 'RecipeHop'},
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
            'Meta': {'object_name': 'RecipeYeast'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ideal': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"}),
            'yeast': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Yeast']"})
        },
        'app.sourcedhopdetails': {
            'Meta': {'object_name': 'SourcedHopDetails'},
            'alpha_acid_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'alpha_acid_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'beta_acid_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'beta_acid_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'caryophyllene_pctg_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'caryophyllene_pctg_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'cohumulone_pctg_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'cohumulone_pctg_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'farnesene_pctg_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'farnesene_pctg_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'humulene_pctg_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'humulene_pctg_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'myrcene_pctg_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'myrcene_pctg_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'oils_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'oils_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'storage_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'storage_label': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'storage_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True'})
        },
        'app.starredrecipe': {
            'Meta': {'object_name': 'StarredRecipe'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipe']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'app.step': {
            'Meta': {'ordering': "['date']", 'object_name': 'Step'},
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
            'Meta': {'object_name': 'Style'},
            'bjcp_code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Style']", 'null': 'True'})
        },
        'app.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pref_brew_type': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '1'}),
            'pref_brewhouse_efficiency': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': "'75'"}),
            'pref_dispensing_style': ('django.db.models.fields.CharField', [], {'default': "'b'", 'max_length': '1'}),
            'pref_make_starter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pref_secondary_ferm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'timezone': ('timezones.fields.TimeZoneField', [], {'default': "'UTC'", 'blank': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'app.yeast': {
            'Meta': {'object_name': 'Yeast'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.YeastManufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '7'})
        },
        'app.yeastmanufacturer': {
            'Meta': {'object_name': 'YeastManufacturer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['app']