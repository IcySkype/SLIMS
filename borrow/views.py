from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Material, ItemInRequest, MaterialRequest, Group, Liability, LabApparelRequest
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from formtools.wizard.views import SessionWizardView
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
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
    form_class = UpdateMaterialDetailsForm
    template_name = 'update_material.html'
    success_url = reverse_lazy('material_list')
    success_message = 'Material updated successfully.'

class StockMaterialView(SuccessMessageMixin, UpdateView):
    model = Material
    form_class = RestockMaterialForm
    template_name = 'restock_material.html'
    success_url = reverse_lazy('material_list')
    success_message = 'Material updated stock successfully.'

class DeleteMaterialView(SuccessMessageMixin, DeleteView):
    model = Material
    template_name = 'delete_material.html'
    success_url = reverse_lazy('material_list')
    success_message = 'Material deleted successfully.'

class MaterialListView(ListView):
    model = Material
    template_name = 'material_list.html'
    context_object_name = 'materials'
    queryset = Material.objects.all()
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(supplier__icontains=search_query) | 
                Q(description__icontains=search_query) | 
                Q(material_type__icontains=search_query)
            )
        return queryset
    
def get_material_details(request):
    material_id = request.GET.get('material_id')  # Get the selected material's ID from the request
    if material_id:
        try:
            material = Material.objects.get(pk=material_id)  # Fetch the material from the database
            # Determine unit options based on the material type
            if material.material_type == 'equipment':
                unit_options = ['None']
            elif material.material_type == 'material':
                unit_options = ['g', 'mg']
            elif material.material_type == 'reagent':
                unit_options = ['mL', 'L']
            else:
                unit_options = []
            return JsonResponse({
                'material_type': material.material_type,
                'description': material.description,
                'unit_options': unit_options,
            })
        except Material.DoesNotExist:
            return JsonResponse({'error': 'Material not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def search_materials(request):
    if request.method == "GET":
        query = request.GET.get('q', '').strip()  # Get the search query
        materials = Material.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(material_type__icontains=query)
        ).values('id', 'name', 'description', 'material_type')[:20]  # Limit results
        return JsonResponse({'materials': list(materials)}, safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)


#view requests:
class RequestListView(ListView):
    model = Request
    template_name = 'request_list_view.html'
    context_object_name = 'requests'
    
    def dispatch(self, *args, **kwargs):
        self.check_and_update_overdue_statuses()
        return super().dispatch(*args, **kwargs)

    def check_and_update_overdue_statuses(self):
        liable_requests = Request.objects.filter(
            status='borrowed',
            request_on_date__lt=timezone.now().date()
        )
        liable_requests_control_numbers = []
        for requests in liable_requests:
            liable_requests_control_numbers.append(requests.control_number)

        stored_liable_requests = Request.objects.filter(
                                control_number__in=liable_requests_control_numbers
                            )
        

        liable_requests.update(status='liable')

        Request.objects.filter(
            status__in=['approved', 'pending_approval'],
            request_on_date__lt=timezone.now().date()
        ).update(status='denied')

        for request in stored_liable_requests:
            if request.request_type == 'material':
                group = request.material_request.groups
                students = group.members.all()
                for student in students:    
                    Liability.objects.get_or_create(
                        request=request,
                        student=student,
                        defaults={"remarks": "Automatically assigned liability for overdue material."},
                    )
            elif request.request_type == 'lab_apparel':
                student = request.lab_apparel_request.student
                Liability.objects.get_or_create(
                    request=request,
                    student=student,
                    defaults={'remarks': f"Liability for lab apparel request {request.control_number}"}
                )
    
    def get_queryset(self):
        user = self.request.user
        
        excluded_statuses = ['denied', 'returned']
        
        if user.user_type == 'teacher':
            return MaterialRequest.objects.filter(
                teacher=user,
            ).exclude(request__status__in=excluded_statuses).distinct()

        elif user.user_type == 'lab_technician':
            material_requests = MaterialRequest.objects.filter(
                teacher_approval=True,
            ).exclude(request__status__in=excluded_statuses)

            
            lab_apparel_requests = LabApparelRequest.objects.all().exclude(request__status__in=excluded_statuses)
            combined_requests = list(material_requests) + list(lab_apparel_requests)
            return combined_requests

        return Request.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_ids = [request.request.control_number for request in context['requests']]
        if self.request.user.user_type == 'teacher': 
            context['material_requests'] = MaterialRequest.objects.filter(
                request__status__in=['pending_approval', 'approved', 'borrowed'],  # Access Request's `status`
                teacher=self.request.user  # Filter by teacher
            )
            context['lab_apparel_requests'] = []
        elif self.request.user.user_type == 'lab_technician':
            context['material_requests'] = MaterialRequest.objects.filter(request__status__in=['approved', 'borrowed', 'liable'], request__in=request_ids)
            context['lab_apparel_requests'] = LabApparelRequest.objects.filter(request__in=request_ids)
        return context

class RequestDetailView(DetailView):
    model = Request
    template_name = "request_detail.html"
    context_object_name = "request"

    def get_object(self):
        # Fetch the request object based on the control_number
        control_number = self.kwargs.get("control_number")
        return get_object_or_404(Request, control_number=control_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_obj = self.object

        try:
            material_request = request_obj.material_request
            context['is_material_request'] = True
            context['material_request'] = material_request
            context['items'] = material_request.items.all()
            context['group'] = material_request.groups
        except MaterialRequest.DoesNotExist:
            context['is_material_request'] = False

        try:
            lab_apparel_request = request_obj.lab_apparel_request
            context['lab_apparel_request'] = lab_apparel_request
        except LabApparelRequest.DoesNotExist:
            context['lab_apparel_request'] = None

        context['teacher_can_approve_or_deny'] = (
            self.request.user.user_type == 'teacher'
            and request_obj.status == 'pending_approval'
        )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not(request.user.is_authenticated):
            return HttpResponseForbidden("Only teachers can take action on this request.")
        if self.object.status != 'pending_approval':
            return HttpResponseForbidden("This request is not pending approval.")

        action = request.POST.get('action')
        print(action)
        try:
            if request.user.user_type == 'teacher':
                material_request = self.object.material_request
                if action == 'approve':
                    material_request.teacher_approval = True
                    self.object.status = 'approved'
                elif action == 'deny':
                    material_request.teacher_approval = False
                    self.object.status = 'denied'
                material_request.save()
                self.object.save()
            elif request.user.user_type == 'lab_technician':
                request_object = self.object.request
                print (self.object)
                if action == 'lend':
                    request_object.status = 'borrowed'
                    self.object.save()
        except MaterialRequest.DoesNotExist:
            return HttpResponseForbidden("This request is not a material request.")

        return redirect('request_detail', control_number=self.object.control_number)


#material return
def return_items(request, control_number):
    # Get the MaterialRequest object by control_number
    material_request = get_object_or_404(MaterialRequest, request__control_number=control_number)
    materials_in_request = ItemInRequest.objects.filter(request=material_request)

    if request.method == 'POST':
        for material_in_request in materials_in_request:
            already_returned = False
            if material_in_request.status == 'returned':
                already_returned = True
            status = request.POST.get(f'status_{material_in_request.id}')
            if status:
                material_in_request.status = status
                material_in_request.save()
            if material_in_request.status == 'returned' and not(already_returned):
                material_in_request.item.stock += material_in_request.quantity
                MaterialUsageLog.objects.create(
                                material=material_in_request.item,
                                action='return',
                                quantity=material_in_request.quantity,
                                remarks=f"Returned in material Request Control No. {material_request.request.control_number}"
                            )
        if any (material_in_request.status == 'broken' for material_in_request in materials_in_request):
            broken_materials = [
                f"{material.item} (qty: {material.quantity})"
                for material in materials_in_request if material.status == 'broken'
            ]
            broken_materials_list = ", ".join(broken_materials)
            for student in material_request.groups.members.all():
                Liability.objects.create(
                    request=material_request.request,
                    student=student,
                    remarks = (
                        f"Control No.: {material_request.request.control_number}. "
                        f"Broken/Lost materials: {broken_materials_list}"
                    )
                )

        # If any item is returned, update the MaterialRequest status to 'returned'
        if all(item.status in ['returned', 'used'] for item in materials_in_request):
            material_request.request.status = 'returned'
            liabilities = Liability.objects.filter(request=material_request.request)
            if liabilities.exists():
                liabilities.update(is_complied=True)
        else:
            material_request.request.status = 'liable'
        material_request.request.save()

        return redirect('request_list')

    return render(request, 'return_items.html', {
        'material_request': material_request,
        'materials_in_request': materials_in_request,
    })

def return_lab_apparel(request, control_number):
    # Get the LabApparelRequest object by control_number
    lab_apparel_request = get_object_or_404(LabApparelRequest, request__control_number=control_number)

    # Check if there are any liabilities for this lab apparel request
    liabilities = Liability.objects.filter(request=control_number)

    # Calculate the penalty if there are liabilities
    penalty = 0
    if liabilities.exists():
        # Calculate the number of days since the item was borrowed
        days_lapsed = (timezone.now().date() - lab_apparel_request.request.request_on_date).days
        if days_lapsed > 0:  # Only calculate if days_lapsed is positive
            penalty = days_lapsed * 10.00  # Currency (e.g., PHP or USD)

    if request.method == 'POST':
        # Set the LabApparelRequest status to 'returned'
        lab_apparel_request.request.status = 'returned'
        lab_apparel_request.request.save()

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
    search_query = None

    if 'search' in request.GET:
        search_query = request.GET['search']
        liabilities = liabilities.filter(
            Q(student__student_id__icontains=search_query) | 
            Q(request__control_number__icontains=search_query)
        )

    return render(request, 'search_liabilities.html', {
        'liabilities': liabilities,
        'search_query': search_query,
    })