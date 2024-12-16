from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import MaterialRequest, ItemInRequest, LabApparelRequest, MaterialUsageLog
from django.urls import reverse

def approve_material_request(request, control_number):
    material_request = get_object_or_404(MaterialRequest, request__control_number=control_number)
    
    if not request.user.is_authenticated or request.user.user_type != 'lab_technician':
        return redirect(f"{reverse('request_list')}?alert=You+are+not+authorized+to+perform+this+action&alert_type=danger") 

    if material_request.request.status in ['pending_approval', 'denied', 'borrowed', 'returned', 'liable']:
        return redirect(f"{reverse('request_list')}?alert=This+request+has+already+been+processed&alert_type=warning")

    if request.method == 'POST':
        approve_request = request.POST.get('approve_request')
        deny_request = request.POST.get('deny_request')
        back = request.POST.get('back')

        if approve_request:
            for item_in_request in material_request.items.all():
                status = request.POST.get(f'status_{item_in_request.id}')
                if status:
                    item_in_request.status = status

                    if status == 'borrowed':
                        item = item_in_request.item
                        if item.stock >= item_in_request.quantity:
                            item.stock -= item_in_request.quantity
                            item.save()
                            MaterialUsageLog.objects.create(
                                material=item,
                                action='usage',
                                quantity=item_in_request.quantity,
                                remarks=f"Used in material Request Control No. {material_request.request.control_number}"
                            )
                        else:
                            item_in_request.status = 'denied'
                            item_in_request.save()
                item_in_request.save()
            denied_items = material_request.items.filter(status='denied')
            if denied_items.count() == material_request.items.count():
                material_request.request.status = 'denied'
                material_request.request.save()
            else:
                material_request.request.lab_technician=request.user
                material_request.request.labtech_approval=True
                material_request.request.save()
            return redirect('request_list')

        elif deny_request:
            for item_in_request in material_request.materials.all():
                item_in_request.status = 'denied'
                item_in_request.save()
            material_request.request.status = 'denied'
            material_request.request.save()
            return redirect('request_list')
        elif back:
            return redirect('request_list')

    materials_in_request = ItemInRequest.objects.filter(request=material_request)

    return render(request, 'check_material_request.html', {
        'material_request': material_request,
        'materials_in_request': materials_in_request
    })

def approve_lab_apparel_request(request, control_number):
    lab_request = get_object_or_404(LabApparelRequest, request__control_number=control_number)

    if request.method == 'POST':
        approve_request = request.POST.get('approve_request')
        deny_request = request.POST.get('deny_request')

        if approve_request:
            print('Uhhh')
            lab_request.request.labtech_approval = True
            lab_request.request.lab_technician = request.user
            lab_request.request.status = 'borrowed'
        elif deny_request:
            lab_request.request.status = 'denied'
        
        lab_request.request.save()
        return redirect('request_list')

    return render(request, 'lab_apparel_approve_borrow_form.html', {'lab_request': lab_request})