from django.db import models
from users.models import User
from django.utils import timezone

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
    quantity = models.PositiveIntegerField()
    MATERIAL_TYPE_CHOICES = [
        ('reagent', 'Reagent'),
        ('material', 'Material'),
        ('equipment', 'Equipment'),
    ]
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES, default='material')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description

# MaterialRequest model
class MaterialRequest(models.Model):
    STATUS_CHOICES = [
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved by Teacher'),
        ('denied', 'Denied'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned')
    ]
    control_number = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, limit_choices_to={'user_type': 'teacher'})
    subject = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    experiment_number = models.CharField(max_length=50)
    group_number = models.CharField(max_length=50)
    date_of_experiment = models.DateField()
    time_of_experiment = models.TimeField()
    title_of_experiment = models.CharField(max_length=200)
    teacher_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests', limit_choices_to={'user_type': 'lab_technician'})#indicates approved by labtech
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending_approval')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Materials Request for {self.subject} - {self.title_of_experiment}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

# Materials in MaterialRequest
class MaterialInRequest(models.Model):
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
        (None, 'None'),
        ('g', 'Grams'), #Mass
        ('mg', 'Milligrams'), #Mass
        ('mL', 'Milliliters'), #Volume
        ('L', 'Liters'), #Volume
        ('mol/L', 'Molarity'), #Moles per L solution, concentration
        ('mol/kg', 'Molality'), #Moles per kg solvent, concentration
        ('%', 'Mass Percentage'),  # % per mass solution (mass percent), concentration
        ('% v/v', 'Volume Percentage'),  # % per volume solution (volume percent), concentration
        ('ppm', 'Parts Per Million')  # solute per 1M parts solution, concentration
    ]
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    request = models.ForeignKey(MaterialRequest, on_delete=models.CASCADE, related_name='materials')
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default=None, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.quantity} of {self.material.name} - {self.status}"

# Group model
class Group(models.Model):
    materials_request = models.ForeignKey(MaterialRequest, on_delete=models.CASCADE, related_name='groups')
    leader = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name='group_leader', null=True)
    members = models.ManyToManyField(Student, related_name='group_member' )

    def __str__(self):
        return f"Group {self.materials_request.group_number}, Leader: {self.leader}"

# LabApparelRequest model
class LabApparelRequest(models.Model):
    STATUS_CHOICES = [
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved by Teacher'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
    ]
    control_number = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_and_year = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    date_borrowed = models.DateField()
    time_borrowed = models.TimeField()
    borrowed_item = models.CharField(max_length=50, choices=[('lab_gown', 'Lab Gown'), ('lab_apron', 'Lab Apron')])
    teacher_approval = models.BooleanField(default=False)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_lab_apparel', limit_choices_to={'user_type': 'teacher'})
    labtech_approval = models.BooleanField(default=False)
    lab_technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='noted_borrow_lab_apparel', limit_choices_to={'user_type': 'lab_technician'})
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending_approval')

    def __str__(self):
        return f"{self.borrowed_item} request by {self.student}"

# Liabilities model
class Liability(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('materials_request', 'Materials Request'),
        ('lab_apparel_request', 'Lab Apparel Request'),
    ]
    request = models.IntegerField()
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES, default='lab_apparel_request')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_complied = models.BooleanField(default=False)
    remarks = models.TextField(default="")

    def __str__(self):
        return f"Liability for Student ID {self.student.student_id} in {self.request_type} Control No. {self.request}"
    

    