# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_newspage_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='newspage',
            old_name='visibility',
            new_name='visible',
        ),
    ]
