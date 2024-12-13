from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import LabApparelRequest, MaterialRequest

def LabApparelApprovalView(request, control_number):
    lab_request = get_object_or_404(LabApparelRequest, control_number=control_number)

    if request.method == "POST":
        if request.user.user_type == 'teacher':
            lab_request.teacher_approval = True
            lab_request.status = 'approved'
            lab_request.save()
        return redirect('request_list')

    return render(request, 'lab_apparel_approval_form.html', {
        'lab_request': lab_request
    })

def MaterialRequestApprovalView(request, control_number):
    material_request = get_object_or_404(MaterialRequest, control_number=control_number)

    if request.method == "POST":
        if request.user.user_type == 'teacher':
            material_request.teacher_approval = True
            material_request.status = 'approved'
            material_request.save()
        return redirect('request_list')

    return render(request, 'material_request_approval_form.html', {
        'material_request': material_request
    })
