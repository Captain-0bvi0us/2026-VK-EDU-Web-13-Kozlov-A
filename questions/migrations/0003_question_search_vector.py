from django.contrib.postgres.search import SearchVectorField
from django.db import migrations


def _create_search_vector_column(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE questions_question "
            "ADD COLUMN IF NOT EXISTS search_vector tsvector"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS questions_question_search_vector_gin "
            "ON questions_question USING GIN (search_vector)"
        )
        cursor.execute(
            "UPDATE questions_question SET search_vector = "
            "setweight(to_tsvector('russian', coalesce(title, '')), 'A') || "
            "setweight(to_tsvector('russian', coalesce(text, '')), 'B')"
        )


def _drop_search_vector_column(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "DROP INDEX IF EXISTS questions_question_search_vector_gin"
        )
        cursor.execute(
            "ALTER TABLE questions_question DROP COLUMN IF EXISTS search_vector"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0002_questionlike_answerlike_value"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="question",
                    name="search_vector",
                    field=SearchVectorField(blank=True, null=True, editable=False),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    _create_search_vector_column,
                    _drop_search_vector_column,
                ),
            ],
        ),
    ]
