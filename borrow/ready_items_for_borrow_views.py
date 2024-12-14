from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import MaterialRequest, ItemInRequest, LabApparelRequest
from django.urls import reverse

def check_and_approve_material_request(request, control_number):
    material_request = get_object_or_404(MaterialRequest, control_number=control_number)
    
    if not request.user.is_authenticated or request.user.user_type != 'lab_technician':
        return redirect(f"{reverse('request_list')}?alert=You+are+not+authorized+to+perform+this+action&alert_type=danger") 

    if material_request.status in ['ready', 'denied', 'borrowed', 'returned']:
        return redirect(f"{reverse('request_list')}?alert=This+request+has+already+been+processed&alert_type=warning")

    if request.method == 'POST':
        approve_request = request.POST.get('approve_request')
        deny_request = request.POST.get('deny_request')

        if approve_request:
            for material_in_request in material_request.materials.all():
                status = request.POST.get(f'status_{material_in_request.id}')
                if status:
                    material_in_request.status = status

                    if status == 'ready':
                        material = material_in_request.material
                        if material.quantity >= material_in_request.quantity:
                            material.quantity -= material_in_request.quantity
                            material.save()
                        else:
                            material_in_request.status = 'denied'
                            material_in_request.save()
                material_in_request.save()
            material_request.status = 'borrowed'
            material_request.approved_by=request.user
            material_request.save()
            return redirect('request_list')

        elif deny_request:
            for material_in_request in material_request.materials.all():
                material_in_request.status = 'denied'
                material_in_request.save()
            material_request.status = 'denied'
            material_request.save()
            return redirect('request_list')

    materials_in_request = ItemInRequest.objects.filter(request=material_request)

    return render(request, 'check_material_request.html', {
        'material_request': material_request,
        'materials_in_request': materials_in_request
    })

def approve_lab_apparel_request(request, control_number):
    lab_request = get_object_or_404(LabApparelRequest, control_number=control_number)

    if request.method == 'POST':
        approve_request = request.POST.get('approve_request')
        deny_request = request.POST.get('deny_request')

        if approve_request:
            lab_request.labtech_approval = True
            lab_request.lab_technician = request.user
            lab_request.status = 'borrowed'
        elif deny_request:
            lab_request.status = 'denied'
        
        lab_request.save()
        return redirect('request_list')

    return render(request, 'lab_apparel_approve_borrow_form.html', {'lab_request': lab_request})
