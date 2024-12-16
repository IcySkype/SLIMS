from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import LabApparelRequest, MaterialRequest, Request

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

def LabTechLending(request, control_number):
    request_object = get_object_or_404(Request, control_number=control_number)

    if request.method == "POST":
        if request.user.user_type == 'lab_technician':
            if request_object.request_type == 'material':
                items = request_object.material_request.items.all()
                for item in items:
                    if item.status == 'approved':
                        item.status = 'borrowed'
                        item.save()
            elif request_object.request_type == 'lab_apparel':
                pass
            request_object.status = 'borrowed'
            request_object.save()
        return redirect('request_list')