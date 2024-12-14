# Generated by Django 5.1.4 on 2024-12-14 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borrow', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('denied', 'Denied'), ('borrowed', 'Borrowed'), ('returned', 'Returned'), ('liable', 'With Liabilities')], default='pending_approval', max_length=50),
        ),
    ]