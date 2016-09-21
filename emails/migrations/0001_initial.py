# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import emails.models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('attached_file', models.FileField(upload_to=emails.models.get_attachment_filename)),
                ('content_type', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='EmailEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('send_at', models.IntegerField(null=True)),
                ('sent', models.BooleanField(default=False)),
                ('customer_id', models.CharField(verbose_name='customer id', max_length=9, blank=True)),
                ('context', jsonfield.fields.JSONField(verbose_name='template context', default={}, blank=True)),
                ('sender', models.CharField(verbose_name='from (can be named format)', max_length=255, blank=True)),
                ('recipients', models.TextField(verbose_name='to (comma separated, can be named format)', blank=True)),
                ('subject', models.TextField(verbose_name='subject', blank=True)),
                ('reply_to', models.TextField(verbose_name='(comma separated, can be named format)', blank=True)),
                ('rendered_template', models.TextField(verbose_name='rendered template')),
                ('rendered_plain_template', models.TextField(verbose_name='plain text template')),
                ('thirdparty_id', models.CharField(max_length=100, blank=True)),
                ('check_url', models.URLField(blank=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='EmailKind',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='email kind name', max_length=255)),
                ('language', models.CharField(verbose_name='language', max_length=2, choices=[('pt', 'Portuguese'), ('es', 'Spanish')], default='es')),
                ('template', models.TextField(verbose_name='template')),
                ('plain_template', models.TextField(verbose_name='plain text template')),
                ('default_context', jsonfield.fields.JSONField(verbose_name='default template context', default={}, blank=True)),
                ('default_sender', models.CharField(verbose_name='default from (can be named format)', max_length=255, blank=True)),
                ('default_recipients', models.TextField(verbose_name='default to (comma separated, can be named format)', blank=True)),
                ('default_subject', models.TextField(verbose_name='default subject', blank=True)),
                ('default_reply_to', models.TextField(verbose_name='default reply to (comma separated, can be named format)', blank=True)),
            ],
            options={
                'ordering': ['name', 'language'],
            },
        ),
        migrations.CreateModel(
            name='EmbeddedImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('placeholder_name', models.CharField(max_length=100)),
                ('content_id', models.CharField(max_length=100, blank=True)),
                ('image', models.ImageField(upload_to=emails.models.get_image_filename)),
                ('kind', models.ForeignKey(to='emails.EmailKind')),
            ],
            options={
                'ordering': ['kind', 'placeholder_name'],
            },
        ),
        migrations.AddField(
            model_name='emailkind',
            name='images',
            field=models.ManyToManyField(to='emails.EmbeddedImage'),
        ),
        migrations.AddField(
            model_name='emailentry',
            name='kind',
            field=models.ForeignKey(to='emails.EmailKind'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='entry',
            field=models.ForeignKey(to='emails.EmailEntry'),
        ),
        migrations.AlterUniqueTogether(
            name='embeddedimage',
            unique_together=set([('kind', 'placeholder_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='emailkind',
            unique_together=set([('name', 'language')]),
        ),
    ]
