# Generated by Django 5.1.4 on 2024-12-16 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borrow', '0006_alter_group_materials_request'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iteminrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('denied', 'Denied'), ('approved', 'Approved'), ('ready', 'Ready'), ('borrowed', 'Borrowed'), ('returned', 'Returned'), ('broken', 'Broken/Lost'), ('used', 'Used')], default='pending', max_length=20),
        ),
    ]