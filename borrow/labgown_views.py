from formtools.wizard.views import SessionWizardView
from django.shortcuts import render, redirect, get_object_or_404
from .models import LabApparelRequest, Student, Request
from .forms import UserAgreementForm, LabApparelRequestForm

FORMS = [
    ('agreement', UserAgreementForm),
    ('lab_apparel_request', LabApparelRequestForm),
]

TEMPLATES = {
    'agreement': 'borrow-agreement-labapparel.html',
    'lab_apparel_request': 'lab-apparel-request-form.html',
}

class LabApparelRequestWizard(SessionWizardView):
    form_list = FORMS

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        agreement_form = form_list[0]
        request_form = form_list[1]

        if agreement_form.cleaned_data['agreement']:
            # Extract data from the form
            first_name = request_form.cleaned_data['first_name']
            last_name = request_form.cleaned_data['last_name']
            student_id = request_form.cleaned_data['student_id']
            student_contact_number = request_form.cleaned_data['contact_number']

            # Check if student exists, create if not
            student, created = Student.objects.get_or_create(
                student_id=student_id,
                defaults={
                    'first_name': first_name,
                    'surname': last_name,
                    'contact_number': student_contact_number,
                }
            )
            request, created2 = Request.objects.get_or_create(
                request_type='lab_apparel',
                request_on_date=request_form.cleaned_data['request_on_date'],
                request_on_time=request_form.cleaned_data['request_on_time']
            )
            # Create the LabApparelRequest object
            lab_apparel_request = LabApparelRequest(
                request=request,
                student=student,
                course_and_year=request_form.cleaned_data['course_and_year'],
                department=request_form.cleaned_data['department'],
                borrowed_item=request_form.cleaned_data['borrowed_item']
            )
            lab_apparel_request.save()
            return redirect('labapparel_request_success', control_number=lab_apparel_request.request.control_number)
        
def labapparel_request_success(request, control_number):
    labapparel_request = get_object_or_404(LabApparelRequest, request__control_number=control_number)
    return render(request, 'labapparel-request-success.html', {'request': labapparel_request})
