# Generated by Django 5.1.4 on 2024-12-16 06:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borrow', '0005_remove_labapparelrequest_date_borrowed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='materials_request',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='borrow.materialrequest'),
        ),
    ]
