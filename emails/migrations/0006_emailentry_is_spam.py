# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0005_auto_20151021_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailentry',
            name='is_spam',
            field=models.BooleanField(default=False, verbose_name='Marked as SPAM'),
        ),
    ]
