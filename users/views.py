from django.shortcuts import render, redirect
from .forms import UserSignupForm, EmailLoginForm, TeacherRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .utils import send_registration_email
from datetime import datetime, timedelta
from django.db.models import Q
from django.utils import timezone
from borrow.models import Request
from collections import OrderedDict


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
    today = timezone.now().date()
    week_end = today + timedelta(days=6)

    if request.user.user_type == 'teacher':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        statuses = ['pending_approval', 'approved']
        requests = Request.objects.filter(
            request_on_date__range=[start_of_week, end_of_week],
            request_type='material',
            status__in=statuses
        ).exclude(
            Q(status='denied') | Q(status='returned')
        ).order_by('request_on_date', 'request_on_time')
        request_m_count = requests.filter(status='pending_approval').count()
        requestcount = requests.count()
        context = {
            'week_start': start_of_week,
            'week_end': end_of_week,
            'requestcount': requestcount,
            'm_count': request_m_count,
        }
        return render(request, 'teacher-dashboard.html', context= context)
    elif request.user.user_type == 'lab_technician':
        # Get the start of the current week (Monday)
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Filter requests for the current week
        requests = Request.objects.filter(
            request_on_date__range=[start_of_week, end_of_week]
        ).exclude(
            Q(status='denied') | Q(status='returned') |
            (Q(request_type='material') & Q(status='pending_approval'))
        ).order_by('request_on_date', 'request_on_time')

        # Initialize schedule with actual weekdays as keys
        week_schedule = OrderedDict(
            (start_of_week + timedelta(days=i), []) for i in range(7)
        )
        # Count material requests
        request_m_count = requests.filter(request_type='material').count()

        # Count lab apparel requests
        request_l_count = requests.filter(request_type='lab_apparel').count()
        requestcount = requests.count()
        # Group requests by their scheduled day
        for req in requests:
            if req.request_on_date in week_schedule:
                week_schedule[req.request_on_date].append({
                    'time': req.request_on_time.strftime('%I:%M %p'),  # Format time
                    'description': f"{req.get_request_type_display()} - {req.get_status_display()}",
                })

        # Ensure all days have the same number of rows (fill with None if necessary)
        max_tasks_per_day = max(len(tasks) for tasks in week_schedule.values())
        for day in week_schedule:
            while len(week_schedule[day]) < max_tasks_per_day:
                week_schedule[day].append(None)

        # Align tasks in a transposed structure: Each row will correspond to a time slot across all days
        aligned_schedule = [
            [week_schedule[day][i] for day in week_schedule]
            for i in range(max_tasks_per_day)
        ]

        # Convert date keys to weekday names for the template
        week_schedule_names = [day.strftime("%A") for day in week_schedule.keys()]

        context = {
            'week_schedule': aligned_schedule,  # Transposed schedule
            'week_schedule_names': week_schedule_names,  # Day names for header
            'week_start': start_of_week,
            'week_end': end_of_week,
            'requestcount': requestcount,
            'm_count': request_m_count,
            'l_count': request_l_count, 
        }
        return render(request, 'labtech-dashboard.html', context = context)
    else:
        return render(request, 'base.html')

def home(request):
    return redirect('login')