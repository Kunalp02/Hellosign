# Generated by Django 4.1.1 on 2022-09-25 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_document_final_copy"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="signing_url",
            field=models.URLField(blank=True, max_length=50, null=True),
        ),
    ]
