# Generated by Django 4.1.5 on 2023-04-12 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0001_client_domain"),
        ("accounts", "0001_tenantuser"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenantuser",
            name="tenants",
            field=models.ManyToManyField(
                blank=True,
                help_text="The tenants this user belongs to.",
                related_name="user_set",
                to="customers.client",
                verbose_name="tenants",
            ),
        ),
    ]
