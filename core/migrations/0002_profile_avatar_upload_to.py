# Generated manually: upload_to с UUID для аватара (ДЗ5)

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=core.models.profile_avatar_upload_to,
                verbose_name="аватар",
            ),
        ),
    ]
