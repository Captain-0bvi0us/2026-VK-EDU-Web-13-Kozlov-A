# Generated manually for VoteSign (+1 / -1) on likes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="answerlike",
            name="value",
            field=models.SmallIntegerField(
                choices=[(-1, "дизлайк"), (1, "лайк")],
                default=1,
                verbose_name="голос",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="questionlike",
            name="value",
            field=models.SmallIntegerField(
                choices=[(-1, "дизлайк"), (1, "лайк")],
                default=1,
                verbose_name="голос",
            ),
            preserve_default=False,
        ),
    ]
