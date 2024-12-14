from django.db import models
from users.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Student(models.Model):
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=50, unique=True)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.surname}, {self.first_name}"


# Materials model
class Material(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    stock = models.PositiveIntegerField()
    MATERIAL_TYPE_CHOICES = [
        ('reagent', 'Reagent'),
        ('material', 'Material'),
        ('equipment', 'Equipment'),
    ]
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES, default='material')
    last_stocked = models.DateField(default=timezone.now)
    last_ordered = models.DateField(default=timezone.now)
    supplier = models.CharField(max_length=255)

    def __str__(self):
        return self.name

#Request model
class Request(models.Model):
    control_number = models.AutoField(primary_key=True)
    REQUEST_TYPE_CHOICES = [
        ('material', 'Material Request'),
        ('lab_apparel', 'Lab Apparel Request'),
    ]
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES)
    request_on_date = models.DateField()
    request_on_time = models.TimeField()
    request_created_on = models.DateTimeField(auto_now_add=True)
    lab_technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='noted_requests', limit_choices_to={'user_type': 'lab_technician'})
    labtech_approval = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('liable', 'With Liabilities')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending_approval')

    def __str__(self):
        return self.control_number

# MaterialRequest model
class MaterialRequest(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name='material_request')
    subject = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    experiment_number = models.CharField(max_length=50)
    group_number = models.CharField(max_length=50)
    title_of_experiment = models.CharField(max_length=200)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, limit_choices_to={'user_type': 'teacher'})
    teacher_approval = models.BooleanField(default=False)

    def __str__(self):
        return f"Materials Request - Control No. {self.request.control_number}"

# Materials in MaterialRequest
class ItemInRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('denied', 'Denied'), 
        ('ready', 'Ready'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('broken', 'Broken/Lost'),
        ('used', 'Used')
    ]
    UNIT_CHOICES = [
        (None, 'N/A'),
        ('g', 'Grams'), #Mass
        ('mg', 'Milligrams'), #Mass
        ('mL', 'Milliliters'), #Volume
        ('L', 'Liters') #Volume
    ]
    item = models.ForeignKey(Material, on_delete=models.CASCADE)
    request = models.ForeignKey(MaterialRequest, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default=None, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def clean(self):
        # Validate unit based on material type
        if self.item.material_type == 'equipment' and self.unit:
            raise ValidationError("Equipment should not have a unit.")
        elif self.item.material_type in ['material', 'reagent'] and not self.unit:
            raise ValidationError("Materials and reagents require a unit.")

    def __str__(self):
        return f"Control No. {self.request.request.control_number} Item: {self.item} qty. {self.quantity}"

# Group model
class Group(models.Model):
    materials_request = models.ForeignKey(MaterialRequest, on_delete=models.CASCADE, related_name='groups')
    leader = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name='group_leader', null=True)
    members = models.ManyToManyField(Student, related_name='group_member' )

    def __str__(self):
        return f"Group {self.materials_request.group_number} for Control No. {self.materials_request.request.control_number}, Leader: {self.leader}"

# LabApparelRequest model
class LabApparelRequest(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name='lab_apparel_request')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_and_year = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    date_borrowed = models.DateField()
    time_borrowed = models.TimeField()
    borrowed_item = models.CharField(
        max_length=50, choices=[('lab_gown', 'Lab Gown'), ('lab_apron', 'Lab Apron')]
    )

    def __str__(self):
        return f"LabApparel - Control No. {self.request.control_number}"

# Liabilities model
class Liability(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_complied = models.BooleanField(default=False)
    remarks = models.TextField(default="")

    def __str__(self):
        return f"Liability for Student ID {self.student.student_id} - Control No. {self.request.control_number}"