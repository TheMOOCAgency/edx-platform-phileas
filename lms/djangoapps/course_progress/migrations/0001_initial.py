# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module_type', models.CharField(default=b'problem', max_length=32, db_index=True, choices=[(b'problem', b'problem'), (b'video', b'video'), (b'html', b'html'), (b'course', b'course'), (b'chapter', b'Section'), (b'sequential', b'Subsection'), (b'library_content', b'Library Content')])),
                ('module_state_key', xmodule_django.models.LocationKeyField(max_length=255, db_column=b'module_id', db_index=True)),
                ('course_id', xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('done', models.CharField(default=b'na', max_length=8, db_index=True, choices=[(b'f', b'FINISHED'), (b'i', b'INCOMPLETE')])),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, db_index=True)),
                ('student', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='studenthistory',
            unique_together=set([('student', 'module_state_key', 'course_id')]),
        ),
    ]
