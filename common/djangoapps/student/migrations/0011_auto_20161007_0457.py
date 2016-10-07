# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0010_userprofile_identity_proof_pdf'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='identity_proof_pdf',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='identity_proof_file_extension',
            field=models.CharField(max_length=4, null=True, blank=True),
        ),
    ]
