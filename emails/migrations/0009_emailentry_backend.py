# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0008_emailentry_datetime_scheduled'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailentry',
            name='backend',
            field=models.CharField(verbose_name='Email Backend', blank=True, max_length=40),
        ),
    ]
