from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Material, MaterialInRequest, MaterialRequest, Group, Liability, LabApparelRequest
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from formtools.wizard.views import SessionWizardView
from django.utils import timezone
import re

#inventory management
class AddMaterialView(SuccessMessageMixin, CreateView):
    model = Material
    form_class = AddMaterialForm
    template_name = 'add_material.html'
    success_url = reverse_lazy('material_list')
    success_message = 'Material added successfully.'

class UpdateMaterialView(SuccessMessageMixin, UpdateView):
    model = Material
    form_class = UpdateMaterialForm
    template_name = 'update_material.html'
    success_url = reverse_lazy('material_list')
    success_message = 'Material updated successfully.'

class DeleteMaterialView(SuccessMessageMixin, DeleteView):
    model = Material
    form_class = DeleteMaterialForm
    template_name = 'delete_material.html'
    success_url = reverse_lazy('material_list')
    success_message = 'Material deleted successfully.'

class MaterialListView(ListView):
    model = Material
    template_name = 'material_list.html'
    context_object_name = 'materials'
    queryset = Material.objects.all()

#view requests:
class RequestListView(ListView):
    template_name = 'request_list_view.html'
    context_object_name = 'requests'

    def get_queryset(self):
        if self.request.user.user_type == 'teacher':
            material_requests = MaterialRequest.objects.filter(teacher=self.request.user)
            lab_apparel_requests = LabApparelRequest.objects.filter(teacher=self.request.user)
        elif self.request.user.user_type == 'lab_technician':
            material_requests = MaterialRequest.objects.filter(teacher_approval=True)
            lab_apparel_requests = LabApparelRequest.objects.filter(teacher_approval=True)
        combined_requests = list(material_requests) + list(lab_apparel_requests)
        return combined_requests

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.user_type == 'teacher':
            material_requests = MaterialRequest.objects.filter(teacher=self.request.user)
            lab_apparel_requests = LabApparelRequest.objects.filter(teacher=self.request.user)
        elif self.request.user.user_type == 'lab_technician':
            material_requests = MaterialRequest.objects.filter(teacher_approval=True)
            lab_apparel_requests = LabApparelRequest.objects.filter(teacher_approval=True)
        
        context['material_requests'] = material_requests
        context['lab_apparel_requests'] = lab_apparel_requests

        context['approved_status'] = ['approved', 'ready', 'returned']
        context['declined_status'] = ['denied', 'borrowed']
        
        return context

#material return

def return_items(request, control_number):
    # Get the MaterialRequest object by control_number
    material_request = get_object_or_404(MaterialRequest, control_number=control_number)
    materials_in_request = MaterialInRequest.objects.filter(request=material_request)

    if request.method == 'POST':
        # Iterate through all MaterialInRequest objects and update their status
        for material_in_request in materials_in_request:
            status = request.POST.get(f'status_{material_in_request.id}')
            if status:
                material_in_request.status = status
                material_in_request.save()

        if any (material_in_request.status == 'broken' for material_in_request in materials_in_request):
            group = Group.objects.get(materials_request=material_request)  # Get associated group
            broken_materials = [
                f"{material.material} (qty: {material.quantity})"
                for material in materials_in_request if material.status == 'broken'
            ]
            broken_materials_list = ", ".join(broken_materials)
            for student in group.members.all():
                Liability.objects.create(
                    request=material_request.control_number,
                    request_type='materials_request',
                    student=student,
                    remarks = (
                        f"Control No.: {material_request.control_number}. "
                        f"Broken/Lost materials: {broken_materials_list}"
                    )
                )

        # If any item is returned, update the MaterialRequest status to 'returned'
        if all(item.status == 'returned' for item in materials_in_request):
            material_request.status = 'returned'
        material_request.save()

        return redirect('request_list')  # Redirect to the request list view after processing

    return render(request, 'return_items.html', {
        'material_request': material_request,
        'materials_in_request': materials_in_request,
    })

def return_lab_apparel(request, control_number):
    # Get the LabApparelRequest object by control_number
    lab_apparel_request = get_object_or_404(LabApparelRequest, control_number=control_number, status='borrowed')

    # Check if there are any liabilities for this lab apparel request
    liabilities = Liability.objects.filter(request=control_number, request_type='lab_apparel_request')

    # Calculate the penalty if there are liabilities
    penalty = 0
    if liabilities.exists():
        # Calculate the number of days since the item was borrowed
        days_lapsed = (timezone.now().date() - lab_apparel_request.date_borrowed).days
        if days_lapsed > 0:  # Only calculate if days_lapsed is positive
            penalty = days_lapsed * 10.00  # Currency (e.g., PHP or USD)

    if request.method == 'POST':
        # Set the LabApparelRequest status to 'returned'
        lab_apparel_request.status = 'returned'
        lab_apparel_request.save()

        # Set is_complied to True for all related liabilities
        for liability in liabilities:
            liability.is_complied = True
            liability.save()

        return redirect('request_list')  # Redirect to the request list or other desired view

    return render(request, 'return_lab_apparel.html', {
        'lab_apparel_request': lab_apparel_request,
        'penalty': penalty,
        'liabilities': liabilities,
    })

from django.db.models import Q

def search_liabilities(request):
    liabilities = Liability.objects.all()
    student_id = None

    if 'student_id' in request.GET:
        student_id = request.GET['student_id']
        liabilities = liabilities.filter(Q(student__student_id__icontains=student_id))  # Case-insensitive search for student ID

    return render(request, 'search_liabilities.html', {
        'liabilities': liabilities,
        'student_id': student_id,
    })

def replace_broken_item(request, liability_id):
    liability = get_object_or_404(Liability, id=liability_id)
    material_request = get_object_or_404(MaterialRequest, control_number=liability.request)
    materials_in_request = material_request.materials.all()
    if request.method == 'POST':
        any_broken = False
        for material_in_request in materials_in_request:
            status_key = f"status_{material_in_request.id}"
            new_status = request.POST.get(status_key)
            if new_status == 'broken':
                any_broken = True
            material_in_request.status = new_status
            material_in_request.save()

        # If no items are broken, mark liability as complied
        if not any_broken:
            liability.is_complied = True
            liability.save()

        return redirect('search_liabilities')

    return render(request, 'update_liability.html', {
        'liability': liability,
        'control_number': material_request.control_number,
        'materialinrequest': materials_in_request,
    })