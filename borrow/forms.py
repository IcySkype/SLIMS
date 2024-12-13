from django import forms
from .models import Material, MaterialRequest, Group, MaterialInRequest, Student, Liability, LabApparelRequest
from users.models import User
from django.forms import modelformset_factory, BaseFormSet
from django.utils import timezone

#Inventory Management Forms
class AddMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'description', 'quantity', 'material_type']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError('Quantity cannot be negative.')
        return quantity

class UpdateMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'description', 'quantity', 'material_type']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError('Quantity cannot be negative.')
        return quantity

class DeleteMaterialForm(forms.Form):
    material_id = forms.IntegerField()

    def clean_material_id(self):
        material_id = self.cleaned_data.get('material_id')
        # Ensure the material exists before attempting deletion
        if not Material.objects.filter(id=material_id).exists():
            raise forms.ValidationError('Material with this ID does not exist.')
        return material_id
    
#Materials Request
class UserAgreementForm(forms.Form):
    agreement = forms.BooleanField(
        label="I agree to the terms and conditions",
        required=True
    )

class MaterialRequestForm(forms.ModelForm):
    class Meta:
        model = MaterialRequest
        fields = ['subject', 'department', 'experiment_number', 'group_number',
                  'title_of_experiment', 'date_of_experiment', 'time_of_experiment', 'teacher']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'experiment_number': forms.TextInput(attrs={'class': 'form-control'}),
            'group_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_experiment': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_of_experiment': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'title_of_experiment': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user.is_authenticated:
            if user.user_type == 'teacher':
                self.fields['teacher'].widget = forms.HiddenInput()
                self.fields['teacher'].initial = user
        else:
            self.fields['teacher'].queryset = User.objects.filter(user_type='teacher')
class MaterialInRequestForm(forms.ModelForm):
    class Meta:
        model = MaterialInRequest
        fields = ['material', 'quantity', 'unit']
    unit = forms.ChoiceField(choices=MaterialInRequest.UNIT_CHOICES, required=False)

MaterialInRequestFormSet = modelformset_factory(
    MaterialInRequest,
    form=MaterialInRequestForm,
    extra=1,
    can_delete=True
)

class GroupMemberForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'surname', 'first_name', 'contact_number']

class BaseGroupMemberFormSet(BaseFormSet):
    def clean(self):
        super().clean()
        if not self.forms:
            raise forms.ValidationError("The group must include at least one member.")

GroupMemberFormSet = modelformset_factory(
    Student,
    form=GroupMemberForm,
    extra=1
)

#return materials
class BulkMaterialReturnForm(forms.ModelForm):
    class Meta:
        model = MaterialInRequest
        fields = ['status']  # We only need to change the 'status' field

    status = forms.ChoiceField(choices=MaterialInRequest.STATUS_CHOICES, required=True)

class BulkReturnForm(forms.Form):
    material_in_requests = forms.ModelMultipleChoiceField(
        queryset=MaterialInRequest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        material_request = kwargs.pop('material_request')
        super().__init__(*args, **kwargs)
        
        # Filter materials related to the specific MaterialRequest
        self.fields['material_in_requests'].queryset = MaterialInRequest.objects.filter(request=material_request)
        
    def save(self, group_members):
        for material_in_request in self.cleaned_data['material_in_requests']:
            # If the status is not 'returned', create liability for all group members
            if material_in_request.status != 'returned':
                for member in group_members:
                    Liability.objects.create(
                        material_request=material_in_request.request,
                        material=material_in_request.material,
                        group_member=member,
                        returned=False
                    )
            else:
                # If returned, update the material status to 'returned'
                material_in_request.status = 'returned'
                material_in_request.save()

#lab aparrel borrow
class LabApparelRequestForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your First Name'}))
    last_name = forms.CharField(label="Last Name", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Last Name'}))
    student_id = forms.CharField(label="Student ID", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your ID Number'}))
    course_and_year = forms.CharField(label="Course and Year", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Course and Year'}))
    department = forms.CharField(label="Department", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Department'}))
    date_borrowed = forms.DateField(label="Date Borrowed", widget=forms.DateInput(attrs={'type': 'date'}))
    time_borrowed = forms.TimeField(label="Time Borrowed", widget=forms.TimeInput(attrs={'type': 'time'}))
    student_contact_number = forms.CharField(label="Contact Number", max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Contact Number'}))
    teacher = forms.ModelChoiceField(queryset=User.objects.filter(user_type='teacher'), label="Teacher")
    borrowed_item = forms.ChoiceField(
        label="Borrowing: ",
        choices=[('lab_gown', 'Lab Gown'), ('lab_apron', 'Lab Apron')],
        widget=forms.RadioSelect
    )

class LabApparelReturnForm(forms.ModelForm):
    class Meta:
        model = LabApparelRequest
        fields = ['status']
    
    STATUS_CHOICES = [
        ('pending_approval', 'Pending Approval'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget = forms.Select(choices=self.STATUS_CHOICES)

class ReportFilterForm(forms.Form):
    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]

    month = forms.ChoiceField(choices=MONTH_CHOICES, label='Month')
    year = forms.IntegerField(label='Year', initial=timezone.now().year)        