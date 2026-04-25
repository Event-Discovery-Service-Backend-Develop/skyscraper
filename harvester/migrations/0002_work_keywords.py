from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("harvester", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="work",
            name="keywords",
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
