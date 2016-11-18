# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_auto_20160914_0555'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='order_num',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
