import csv
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.utils import timezone
from .models import Material, Liability, Student, MaterialRequest, MaterialUsageLog, Request
from .forms import ReportFilterForm

def report_selection(request):
    # Check if report type is selected
    report_type = request.GET.get('report_type')

    if report_type == 'material_usage':
        return redirect('material_usage_report')
    elif report_type == 'student_requests':
        return redirect('requests_report')
    elif report_type == 'liabilities':
        return redirect('liabilities_report')
    else:
        return render(request, 'report_selection.html', {
            'error': 'Please select a valid report type.'
        })


def material_usage_report(request):
    logs = MaterialUsageLog.objects.all().order_by('-date')  # List logs, most recent first

    # You can also filter by date range, material, or action type
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        logs = logs.filter(date__range=[start_date, end_date])

    return render(request, 'material_usage_report.html', {'logs': logs})

def export_material_usage_report(request):
    # Fetch all the logs (you can apply filters here as needed)
    logs = MaterialUsageLog.objects.all().order_by('-date')

    # Create an HTTP response with content type for CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="material_usage_report.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['Material', 'Action', 'Quantity', 'Date', 'Remarks'])

    # Write the data rows
    for log in logs:
        writer.writerow([log.material.name, log.get_action_display(), log.quantity, log.date, log.remarks])

    return response

def liabilities_report(request):
    # Get filter parameters from the request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Initialize liabilities queryset
    liabilities = Liability.objects.all()

    # Apply date range filter
    if start_date and end_date:
        liabilities = liabilities.filter(request__request_request_on_date__range=[start_date, end_date])
    elif start_date:  # Only start date is provided
        liabilities = liabilities.filter(request__request_request_on_date__gte=start_date)
    elif end_date:  # Only end date is provided
        liabilities = liabilities.filter(request__request_request_on_date__lte=end_date)

    context = {
        'liabilities': liabilities,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'liabilities_report.html', context)

def liabilities_report_csv(request):
    # Initialize liabilities queryset
    liabilities = Liability.objects.all().select_related('request', 'student')

    # Get filter parameters from the request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Apply date range filter
    if start_date and end_date:
        liabilities = liabilities.filter(request__request_request_on_date__range=[start_date, end_date])
    elif start_date:  # Only start date is provided
        liabilities = liabilities.filter(request__request_request_on_date__gte=start_date)
    elif end_date:  # Only end date is provided
        liabilities = liabilities.filter(request__request_request_on_date__lte=end_date)

    # Set up the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="liabilities_report.csv"'

    # Write CSV header
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Control No.', 'Complied', 'Remarks'])

    # Write data rows
    for liability in liabilities:
        writer.writerow([
            liability.student.student_id,
            str(liability.student),
            liability.request.control_number,
            'Yes' if liability.is_complied else 'No',
            liability.remarks or 'N/A'
        ])

    return response

def requests_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    filter_status = ['returned', 'liable']
    requests = Request.objects.filter(status__in=filter_status)

    if start_date and end_date:
        requests = requests.filter(request_request_on_date__range=[start_date, end_date])
    elif start_date:
        requests = requests.filter(request_request_on_date__gte=start_date)
    elif end_date:
        requests = requests.filter(request_request_on_date__lte=end_date)

    context = {
        'requests': requests,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'requests_report.html', context)

def requests_report_csv(request):
    requests = Request.objects.all().select_related('lab_technician')

    # Filter requests based on date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        requests = requests.filter(request_request_on_date__range=[start_date, end_date])
    elif start_date:
        requests = requests.filter(request_request_on_date__gte=start_date)
    elif end_date:
        requests = requests.filter(request_request_on_date__lte=end_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="requests_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Control No.', 'Request Type', 'Request Date', 'Lab Technician', 'Status'])

    for req in requests:
        writer.writerow([
            req.control_number,
            req.get_request_type_display(),
            req.request_created_on,
            req.lab_technician,
            req.get_status_display()
        ])

    return response