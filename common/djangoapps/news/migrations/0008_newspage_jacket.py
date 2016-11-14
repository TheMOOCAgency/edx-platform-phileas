# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0007_newspage_order_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='jacket',
            field=models.FileField(null=True, upload_to=b'jacket'),
        ),
    ]
