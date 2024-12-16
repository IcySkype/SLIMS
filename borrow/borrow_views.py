from .models import Group
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from formtools.wizard.views import SessionWizardView
from django.contrib import messages

#Materials request
class MaterialsRequestWizard(SessionWizardView):
    FORMS = [
        UserAgreementForm,
        MaterialRequestForm,
        MaterialInRequestFormSet,
        GroupMemberFormSet
    ]
    TEMPLATES_student = {
        "0": "borrow-agreement-student.html",
        "1": "material-form-student.html",
        "2": "materials-in-request-student.html",
        "3": "group-members-student.html"
    }
    TEMPLATES_teacher = {
        "0": "borrow-agreement-teacher.html",
        "1": "material-form-teacher.html",
        "2": "materials-in-request-teacher.html",
        "3": "group-members-teacher.html"
    }

    form_list = FORMS

    def get_form_kwargs(self, step):
        kwargs = super().get_form_kwargs(step)
        if step == '1':
            kwargs['user'] = self.request.user
        elif step == '2':
            kwargs['queryset'] = ItemInRequest.objects.none()  # Ensure no data is prefilled
        elif step == '3':
            kwargs['queryset'] = Student.objects.none()  # Ensure no students are prefilled
        return kwargs

    def get_template_names(self):
        user = self.request.user
        templates = self.TEMPLATES_teacher if user.is_authenticated and user.user_type == 'teacher' else self.TEMPLATES_student
        return [templates[self.steps.current]]

    def done(self, form_list, **kwargs):
        # Step 1: Save MaterialRequestForm
        material_request_form = form_list[1]
        material_request = material_request_form.save(commit=False)

        if self.request.user.is_authenticated and self.request.user.user_type == 'teacher':
            material_request.teacher = self.request.user
            material_request.teacher_approval = True
        material_request.save()

        # Step 2: Save MaterialInRequest FormSet
        materials_in_request_formset = form_list[2]
        print(materials_in_request_formset.cleaned_data)
        for form in materials_in_request_formset:
            material_in_request = form.save(commit=False)
            material_in_request.request = material_request
            material_in_request.save()

        # Step 3: Save Group Member Information
        group_member_formset = form_list[3]
        group_members = []
        for form in group_member_formset:
            if form.cleaned_data:
                student, created = Student.objects.get_or_create(
                    student_id=form.cleaned_data['student_id'],
                    defaults={
                        'surname': form.cleaned_data['surname'],
                        'first_name': form.cleaned_data['first_name'],
                        'contact_number': form.cleaned_data['contact_number']
                    }
                )
                group_members.append(student)

        if group_members:
            leader = group_members[0]
            group = Group.objects.create(materials_request=material_request, leader=leader)
            group.members.set(set(group_members))

        # Step 4: Add Success Message and Redirect
        if self.request.user.is_authenticated and self.request.user.user_type == 'teacher':
            messages.success(self.request, f"Material request successfully created with control number {material_request.request.control_number}.")
            return redirect('request_list')
        else:
            messages.success(self.request, f"Material request successfully created. Control number: {material_request.request.control_number}.")
            return redirect('material_request_success', control_number=material_request.request.control_number)


def material_request_success(request, control_number):
    material_request = get_object_or_404(MaterialRequest, request__control_number=control_number)
    
    if request.user.is_authenticated and request.user.user_type == 'teacher':
        
        return render(request, 'materials-request-success-teacher.html', {
            'materials_request': material_request
        })
    else:
        print(material_request.request.control_number)
        return render(request, 'materials-request-success-student.html', {
            'materials_request': material_request
        })