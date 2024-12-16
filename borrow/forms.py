from django import forms
from .models import Material, MaterialRequest, Group, ItemInRequest, Student, Liability, LabApparelRequest, Request, MaterialUsageLog
from users.models import User
from django.forms import modelformset_factory, BaseFormSet
from django.utils import timezone
from django.core.exceptions import ValidationError
#Inventory Management Forms
class AddMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'material_type', 'description', 'stock', 'supplier', 'last_stocked', 'last_ordered']
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter material name'}),
        required=True
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter material description'}),
        required=True
    )
    stock = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter stock quantity'}),
        required=True
    )
    material_type = forms.ChoiceField(
        choices=Material.MATERIAL_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    supplier = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter supplier name'}),
        required=True
    )
    last_stocked = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Enter date stocked (YYYY-MM-DD)', 'type': 'date'}),
        required=True
    )
    last_ordered = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Enter date ordered (YYYY-MM-DD)', 'type': 'date'}),
        required=True
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['last_stocked'].initial = timezone.now().date()
            self.fields['last_ordered'].initial = timezone.now().date()
    def clean_quantity(self):
        quantity = self.cleaned_data.get('stock')
        if quantity < 0:
            raise forms.ValidationError('Stock cannot be negative.')
        return quantity

class UpdateMaterialDetailsForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'description', 'material_type', 'supplier']
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter material name'}),
        required=True
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter material description'}),
        required=True
    )
    material_type = forms.ChoiceField(
        choices=Material.MATERIAL_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    supplier = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter supplier name'}),
        required=True
    )
        
    def __init__(self, *args, **kwargs):
        super(UpdateMaterialDetailsForm, self).__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class RestockMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['stock', 'last_stocked', 'last_ordered']
    stock = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter stock quantity'}),
        required=True
    )
    last_stocked = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Enter date stocked (YYYY-MM-DD)', 'type': 'date'}),
        required=True
    )
    last_ordered = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Enter date ordered (YYYY-MM-DD)', 'type': 'date'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_stocked'].initial = timezone.now()
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError('Stock cannot be negative.')
        return stock

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.stock += self.cleaned_data['stock']
        instance.last_stocked = timezone.now()

        MaterialUsageLog.objects.create(
        material=instance,
        action='restock',
        quantity=self.cleaned_data['stock'],
        remarks="Restocked via form submission"
        )
        if commit:
            instance.save()
        return instance
    
#Materials Request
class UserAgreementForm(forms.Form):
    agreement = forms.BooleanField(
        required=True
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'checkbox-control'

class MaterialRequestForm(forms.ModelForm):
    request_on_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now().date()
    )
    request_on_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        initial=timezone.now().time()
    )
    class Meta:
        model = MaterialRequest
        fields = [
            'subject',
            'department',
            'experiment_number',
            'group_number',
            'title_of_experiment',
            'teacher'
        ]
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject name'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter department name'}),
            'experiment_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter experiment number'}),
            'group_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter group number'}),
            'title_of_experiment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title of experiment'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.initial['user'] = user
        if user and user.is_authenticated:
            if user.user_type == 'teacher':
                self.fields['teacher'].widget = forms.HiddenInput()
                self.fields['teacher'].initial = user
            else:
                self.fields['teacher'].queryset = User.objects.filter(user_type='teacher')

    def clean(self):
        cleaned_data = super().clean()
        request_on_date = cleaned_data.get('request_on_date')
        
        # Check if the user is anonymous/guest user and validate the date
        user = self.initial.get('user', None)
        if user and user.is_authenticated is False:
            # Ensure request_on_date is at least 2 days in the future
            if request_on_date and request_on_date < timezone.now().date() + timezone.timedelta(days=2):
                raise ValidationError('The request date must be at least 2 days from today for student users.')

        return cleaned_data

    def save(self, commit=True):
        material_request = super().save(commit=False)
        user = self.initial.get('user', None)
        if user.is_authenticated:
            if user.user_type == "teacher":
                request_status = "approved"
            else:
                request_status = "pending_approval"
        else:
            request_status = "pending_approval"

        request = Request.objects.create(
            request_type='material',
            request_on_date=self.cleaned_data['request_on_date'],
            request_on_time=self.cleaned_data['request_on_time'],
            lab_technician=None,
            status=request_status
        )
        material_request.request = request

        if commit:
            material_request.save()
        return material_request

class MaterialInRequestForm(forms.ModelForm):
    material_type = forms.CharField(
        max_length=20,
        disabled=True,  # Disable input
        required=False
    )
    material_description = forms.CharField(
        max_length=255,
        disabled=True,  # Disable input
        required=False
    )

    class Meta:
        model = ItemInRequest
        fields = ['item', 'material_type', 'material_description', 'quantity', 'unit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].widget.attrs.update({"class": "form-select"})
        self.fields['unit'].widget.attrs.update({"class": "form-select"})
        self.fields['quantity'].widget.attrs.update({"class": "form-control", "min": "1"}) 
        material = self.instance.item if self.instance.pk else None
        if material:
            # Automatically populate material_type and material_description based on selected material
            self.fields['material_type'].initial = material.material_type
            self.fields['material_description'].initial = material.description

            if material.material_type == 'equipment':
                self.fields['unit'].choices = ['None']
            elif material.material_type == 'material':
                self.fields['unit'].choices = [(choice[0], choice[1]) for choice in ItemInRequest.UNIT_CHOICES if choice[0] in ['g', 'mg']]
            elif material.material_type == 'reagent':
                self.fields['unit'].choices = [(choice[0], choice[1]) for choice in ItemInRequest.UNIT_CHOICES if choice[0] in ['mL', 'L']]

MaterialInRequestFormSet = modelformset_factory(
    ItemInRequest,
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
        members = []
        for form in self.forms:
            if form.cleaned_data:
                student_id = form.cleaned_data.get('student_id')
                if student_id in members:
                    raise forms.ValidationError(f"Duplicate student ID {student_id} found.")
                members.append(student_id)
        if not members:
            raise forms.ValidationError("The group must include at least one member.")

GroupMemberFormSet = modelformset_factory(
    Student,
    form=GroupMemberForm,
    extra=1
)

#lab aparrel borrow
class LabApparelRequestForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your First Name'}))
    last_name = forms.CharField(label="Last Name", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Last Name'}))
    student_id = forms.CharField(label="Student ID", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your ID Number'}))
    course_and_year = forms.CharField(label="Course and Year", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Course and Year'}))
    department = forms.CharField(label="Department", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Department'}))
    request_on_date= forms.DateField(label="Date Borrowed", widget=forms.DateInput(attrs={'type': 'date'}))
    request_on_time = forms.TimeField(label="Time Borrowed", widget=forms.TimeInput(attrs={'type': 'time'}))
    contact_number = forms.CharField(label="Contact Number", max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Contact Number'}))
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