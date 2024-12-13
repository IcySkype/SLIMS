from django.shortcuts import render, redirect
from .forms import UserSignupForm, EmailLoginForm, TeacherRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .utils import send_registration_email
# Signup View
def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('dashboard')
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = TeacherRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'teacher'
            user.save()
            #send_registration_email(user, form.cleaned_data['password1'])
            messages.success(request, 'Registration successful! Teacher user was created.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TeacherRegisterForm()

    return render(request, 'register.html', {'form': form})

# Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, 'Invalid credentials')
    else:
        form = EmailLoginForm()
    return render(request, 'login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)  # Logs the user out
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

# Dashboard View (After Login)
def dashboard_view(request):
    if request.user.user_type == 'teacher':
        return render(request, 'teacher-dashboard.html')
    elif request.user.user_type == 'lab_technician':
        return render(request, 'labtech-dashboard.html')
    else:
        return render(request, 'base.html')

def home(request):
    return redirect('login')