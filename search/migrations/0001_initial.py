# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-15 09:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SearchIndexLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('document_count', models.IntegerField(default=0)),
            ],
        ),
    ]
