import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from .models import Material, Liability, Student, MaterialRequest
from .forms import ReportFilterForm

def generate_report(request):
    # Default to current month and year
    today = timezone.now()
    current_month = today.month
    current_year = today.year

    # Create the report form
    form = ReportFilterForm(request.GET or None)

    # If the form is valid, process the selected month and year
    if form.is_valid():
        month = form.cleaned_data['month']
        year = form.cleaned_data['year']
    else:
        # Default to current month and year if form is not valid
        month = current_month
        year = current_year

    # Get the materials (inventory)
    materials = Material.objects.all()

    # Get the liabilities for the selected month and year
    liabilities = Liability.objects.filter(
        material_request__created_at__month=month,
        material_request__created_at__year=year
    )

    # Get students with liabilities (who haven't returned items)
    students_with_liabilities = set()
    for liability in liabilities:
        if not liability.returned:
            students_with_liabilities.add(liability.group_member)

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{year}-{month:02d}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Inventory Report'])
    writer.writerow(['Name', 'Description', 'Quantity', 'Material Type', 'Date Added'])

    for material in materials:
        writer.writerow([material.name, material.description, material.quantity, material.get_material_type_display(), material.date_added.strftime('%Y-%m-%d')])

    writer.writerow(['\n', '\n'])
    writer.writerow(['Students with Liabilities'])
    writer.writerow(['Student Name', 'Student ID', 'Material', 'Request ID', 'Status'])

    for student in students_with_liabilities:
        student_name = f"{student.surname}, {student.first_name}"
        for liability in liabilities.filter(group_member=student):
            material = liability.material
            request = liability.material_request
            writer.writerow([student_name, student.student_id, material.name, request.control_number, 'Pending' if not liability.returned else 'Returned'])

    return response
