from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Work",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("openalex_id", models.CharField(db_index=True, max_length=64, unique=True)),
                ("title", models.CharField(blank=True, max_length=1024, null=True)),
                ("doi", models.CharField(blank=True, db_index=True, max_length=256, null=True)),
                ("publication_year", models.IntegerField(blank=True, db_index=True, null=True)),
                ("raw_json", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "works",
                "ordering": ["-created_at"],
            },
        ),
    ]
