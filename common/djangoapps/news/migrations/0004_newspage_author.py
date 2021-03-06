# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0003_auto_20160822_0632'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='author',
            field=models.ForeignKey(default=5, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
