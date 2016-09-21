# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0003_auto_20150721_0906'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailkind',
            name='description',
            field=models.CharField(max_length=300, verbose_name='description', default=''),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='entry',
            field=models.ForeignKey(to='emails.EmailEntry', related_name='attachments'),
        ),
        migrations.AlterField(
            model_name='emailentry',
            name='recipients',
            field=models.TextField(verbose_name='to', blank=True),
        ),
        migrations.AlterField(
            model_name='emailentry',
            name='reply_to',
            field=models.TextField(verbose_name='reply to', blank=True),
        ),
        migrations.AlterField(
            model_name='emailentry',
            name='sender',
            field=models.CharField(max_length=255, verbose_name='from', blank=True),
        ),
    ]
