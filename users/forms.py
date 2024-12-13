from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class UserSignupForm(UserCreationForm):
    user_type_choices = [
        ('teacher', 'Teacher'),
        ('lab_technician', 'Lab Technician'),
    ]
    user_type = forms.ChoiceField(choices=user_type_choices, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'user_type']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user
    
class TeacherRegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        required=True,
    )
    id_num = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your ID Number'}),
        required=True,
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'id_num', 'password1', 'password2']
    

class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'email',
        }),
        label="Email",
        required=True,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id': 'password',
        }),
        label="Password",
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError("Invalid email or password.")
        return cleaned_data