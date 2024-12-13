# Generated by Django 5.1.4 on 2024-12-12 16:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borrow', '0006_drop_liability'),
    ]

    operations = [
        migrations.CreateModel(
            name='Liability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request', models.IntegerField()),
                ('request_type', models.CharField(choices=[('materials_request', 'Materials Request'), ('lab_apparel_request', 'Lab Apparel Request')], default='lab_apparel_request', max_length=50)),
                ('is_complied', models.BooleanField(default=False)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='borrow.student')),
            ],
        ),
    ]
