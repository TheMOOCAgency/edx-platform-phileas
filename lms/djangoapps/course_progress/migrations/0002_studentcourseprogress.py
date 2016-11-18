# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import util.models
import django.utils.timezone
from django.conf import settings
import model_utils.fields
import xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course_progress', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentCourseProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('course_id', xmodule_django.models.CourseKeyField(unique=True, max_length=255, verbose_name=b'Course ID', db_index=True)),
                ('overall_progress', models.FloatField(default=0.0)),
                ('progress_json', util.models.CompressedTextField(null=True, verbose_name=b'Progress JSON', blank=True)),
                ('student', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
