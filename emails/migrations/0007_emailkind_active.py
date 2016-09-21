# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0006_emailentry_is_spam'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailkind',
            name='active',
            field=models.BooleanField(verbose_name='Is active', default=True),
        ),
    ]
