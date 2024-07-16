# Generated by Django 4.1 on 2024-06-28 09:37

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Material",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("material_code", models.CharField(max_length=100)),
                ("batch_code", models.CharField(max_length=100)),
                ("storage_location", models.CharField(max_length=100)),
                ("material_description", models.TextField()),
                ("quantity", models.FloatField()),
                ("unit_of_measure", models.CharField(max_length=50)),
                ("value", models.FloatField()),
                ("department", models.CharField(max_length=100)),
                ("batch_date", models.DateField()),
                ("party_name", models.CharField(blank=True, max_length=100, null=True)),
                ("remarks", models.TextField(blank=True, null=True)),
                ("date_of_clearing", models.DateField(blank=True, null=True)),
                ("person", models.CharField(blank=True, max_length=100, null=True)),
                ("batch_ageing", models.IntegerField()),
                ("material_broad_group_desc", models.CharField(max_length=100)),
            ],
            options={
                "unique_together": {("material_code", "batch_code")},
            },
        ),
    ]
