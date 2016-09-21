# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0002_auto_20150720_0813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailentry',
            name='customer_id',
            field=models.CharField(max_length=30, blank=True, verbose_name='customer id'),
        ),
    ]
