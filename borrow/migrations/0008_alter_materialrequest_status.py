# Generated by Django 5.1.4 on 2024-12-12 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borrow', '0007_liability'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialrequest',
            name='status',
            field=models.CharField(choices=[('pending_approval', 'Pending Approval'), ('approved', 'Approved by Teacher'), ('denied', 'Denied'), ('borrowed', 'Borrowed'), ('returned', 'Returned')], default='pending_approval', max_length=50),
        ),
    ]
