# Generated by Django 5.1.4 on 2024-12-14 04:09

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='LabApparelRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_and_year', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('date_borrowed', models.DateField()),
                ('time_borrowed', models.TimeField()),
                ('borrowed_item', models.CharField(choices=[('lab_gown', 'Lab Gown'), ('lab_apron', 'Lab Apron')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Liability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_complied', models.BooleanField(default=False)),
                ('remarks', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('stock', models.PositiveIntegerField()),
                ('material_type', models.CharField(choices=[('reagent', 'Reagent'), ('material', 'Material'), ('equipment', 'Equipment')], default='material', max_length=20)),
                ('last_stocked', models.DateField(default=django.utils.timezone.now)),
                ('last_ordered', models.DateField(default=django.utils.timezone.now)),
                ('supplier', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='MaterialRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('experiment_number', models.CharField(max_length=50)),
                ('group_number', models.CharField(max_length=50)),
                ('title_of_experiment', models.CharField(max_length=200)),
                ('teacher_approval', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('control_number', models.AutoField(primary_key=True, serialize=False)),
                ('request_type', models.CharField(choices=[('material', 'Material Request'), ('lab_apparel', 'Lab Apparel Request')], max_length=50)),
                ('request_on_date', models.DateField()),
                ('request_on_time', models.TimeField()),
                ('request_created_on', models.DateTimeField(auto_now_add=True)),
                ('labtech_approval', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('pending_approval', 'Pending Approval'), ('approved', 'Approved by Teacher'), ('denied', 'Denied'), ('borrowed', 'Borrowed'), ('returned', 'Returned')], default='pending_approval', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surname', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('student_id', models.CharField(max_length=50, unique=True)),
                ('contact_number', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='ItemInRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('unit', models.CharField(choices=[(None, 'N/A'), ('g', 'Grams'), ('mg', 'Milligrams'), ('mL', 'Milliliters'), ('L', 'Liters')], default=None, max_length=20, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('denied', 'Denied'), ('ready', 'Ready'), ('borrowed', 'Borrowed'), ('returned', 'Returned'), ('broken', 'Broken/Lost'), ('used', 'Used')], default='pending', max_length=20)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='borrow.material')),
            ],
        ),
    ]
