# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0004_auto_20150924_0812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailentry',
            name='deleted',
            field=models.BooleanField(verbose_name='Marked for deletion', db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='emailentry',
            name='sent',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
