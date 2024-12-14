from django.urls import path
from . import views, borrow_views, labgown_views, approval_views, ready_items_for_borrow_views, reports_views

urlpatterns = [
    path('materials/', view=views.MaterialListView.as_view(), name='material_list'),
    path('materials/add/', view=views.AddMaterialView.as_view(), name='add_material'),
    path('materials/<int:pk>/update/', view=views.UpdateMaterialView.as_view(), name='update_material'),
    path('materials/<int:pk>/stock/', view=views.StockMaterialView.as_view(), name='stock_material'),
    path('materials/<int:pk>/delete/', view=views.DeleteMaterialView.as_view(), name='delete_material'),

    path('borrow/', view=borrow_views.MaterialsRequestWizard.as_view(), name='borrow'),
    path('borrow/success/<int:control_number>', view=borrow_views.material_request_success, name='material_request_success'),
    path('borrow_lab_apparel/', view=labgown_views.LabApparelRequestWizard.as_view(), name='lab_gown_request'),
    path('borrow_lab_apparel/success/<int:control_number>', view=labgown_views.labapparel_request_success, name='labapparel_request_success'),

    path('my-requests/', view=views.RequestListView.as_view(), name='request_list'),
    path('approve/lab_apparel/<int:control_number>', view=approval_views.LabApparelApprovalView, name='approve_lab_gown'),
    path('approval/material-request/<int:control_number>/', view=approval_views.MaterialRequestApprovalView, name='approve_material_request'),

    path('my-requests/material-request/<int:control_number>/', view=ready_items_for_borrow_views.check_and_approve_material_request, name='check_and_approve_material_request'),
    path('my-requests/lab_apparel/<int:control_number>/', view=ready_items_for_borrow_views.approve_lab_apparel_request, name='approve_lab_apparel_request'),

    path('return_items/<int:control_number>/', views.return_items, name='return_items'),
    path('return_labapparel/<int:control_number>/', views.return_lab_apparel, name='return_lab_apparel'),

    path('search_liabilities/', views.search_liabilities, name='search_liabilities'),
    path('replace_item/<int:liability_id>/', views.replace_broken_item, name='replace_broken_item'),
]