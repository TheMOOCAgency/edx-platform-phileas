# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='title',
            field=models.CharField(default='First Page', max_length=30),
            preserve_default=False,
        ),
    ]
