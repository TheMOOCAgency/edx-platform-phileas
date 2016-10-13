# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import util.models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_email', '0005_move_target_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseemail',
            name='selected_emails',
            field=util.models.CompressedTextField(null=True, verbose_name=b'Selected Emails', blank=True),
        ),
        migrations.AlterField(
            model_name='target',
            name='target_type',
            field=models.CharField(max_length=64, choices=[(b'myself', b'Myself'), (b'staff', b'Staff and instructors'), (b'learners', b'All students'), (b'selected', b'Selected'), (b'cohort', b'Specific cohort')]),
        ),
    ]
