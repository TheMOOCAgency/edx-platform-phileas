# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0009_userprofile_identity_proof_uploaded_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='identity_proof_pdf',
            field=models.BooleanField(default=0),
        ),
    ]
