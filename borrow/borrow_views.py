from .models import Group
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from formtools.wizard.views import SessionWizardView

    #Materials request
class MaterialsRequestWizard(SessionWizardView):
    FORMS = [UserAgreementForm,
                MaterialRequestForm,
                MaterialInRequestFormSet,
                GroupMemberFormSet
                ]
    TEMPLATES_student = {"0": "borrow-agreement-student.html",
                            "1": "material-form-student.html",
                            "2": "materials-in-request-student.html",
                            "3": "group-members-student.html"
                            }

    TEMPLATES_teacher = {"0": "borrow-agreement-teacher.html",
                            "1": "material-form-teacher.html",
                            "2": "materials-in-request-teacher.html",
                            "3": "group-members-teacher.html"
                            }
    form_list = FORMS
    def get_form_kwargs(self, step):
        kwargs = super().get_form_kwargs(step)
        if step == '1':
            kwargs['user'] = self.request.user
        if step == '2':
            kwargs['queryset'] = MaterialInRequest.objects.none()
        if step == '3':
            kwargs['queryset'] = Student.objects.none()

        return kwargs
    
    def get_template_names(self):
        # Determine if the user is a student or teacher
        user = self.request.user
        if user.is_authenticated and user.user_type == 'teacher':
            templates = self.TEMPLATES_teacher
        else:
            templates = self.TEMPLATES_student
        return [templates[self.steps.current]]

    def done(self, form_list, **kwargs):
        # Step 1: Save MaterialRequestForm
        material_request_form = form_list[1]
        material_request = material_request_form.save(commit=False)
        print(material_request)
        if self.request.user.is_authenticated and self.request.user.user_type == 'teacher':
            material_request.teacher = self.request.user
            material_request.teacher_approval = True
        
        material_request.save()

        # Step 2: Save MaterialInRequestFormSet
        materials_in_request_formset = form_list[2]
        for form in materials_in_request_formset:
            material_in_request = form.save(commit=False)
            material_in_request.request = material_request
            material_in_request.save()

        # Step 3: Create group with students
        group_member_formset = form_list[3]
        group_members = []

        for form in group_member_formset:
            student_id = form.cleaned_data['student_id']
            surname = form.cleaned_data['surname']
            first_name = form.cleaned_data['first_name']
            contact_number = form.cleaned_data['contact_number']

            # Check if the student exists in the database
            student, created = Student.objects.get_or_create(
                student_id=student_id,
                defaults={
                    'surname': surname,
                    'first_name': first_name,
                    'contact_number': contact_number,
                }
            )
            group_members.append(student)
        if group_members:
            # Create a new group
            leader = group_members[0]
            group = Group.objects.create(materials_request=material_request, leader=leader)

            # Add all members to the group
            group.members.set(group_members)

        return redirect('material_request_success', control_number=material_request.control_number)

def material_request_success(request, control_number):
    material_request = get_object_or_404(MaterialRequest, control_number=control_number)
    
    if request.user.is_authenticated and request.user.user_type == 'teacher':
        return render(request, 'materials-request-success-teacher.html', {
            'materials_request': material_request
        })
    else:
        return render(request, 'materials-request-success-student.html', {
            'materials_request': material_request
        })