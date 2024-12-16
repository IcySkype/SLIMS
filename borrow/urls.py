from django.urls import path
from . import labtech_approval_views, views, borrow_views, labgown_views, approval_views, reports_views

urlpatterns = [
    path('materials/', view=views.MaterialListView.as_view(), name='material_list'),
    path('materials/add/', view=views.AddMaterialView.as_view(), name='add_material'),
    path('materials/<int:pk>/update/', view=views.UpdateMaterialView.as_view(), name='update_material'),
    path('materials/<int:pk>/stock/', view=views.StockMaterialView.as_view(), name='stock_material'),
    path('materials/<int:pk>/delete/', view=views.DeleteMaterialView.as_view(), name='delete_material'),
    path('get-material-details/', view=views.get_material_details, name='get_material_details'), #AJAX server side request

    path('borrow/', view=borrow_views.MaterialsRequestWizard.as_view(), name='borrow'),
    path('borrow/success/<int:control_number>', view=borrow_views.material_request_success, name='material_request_success'),
    path('borrow_lab_apparel/', view=labgown_views.LabApparelRequestWizard.as_view(), name='lab_gown_request'),
    path('borrow_lab_apparel/success/<int:control_number>', view=labgown_views.labapparel_request_success, name='labapparel_request_success'),

    path('requests/', view=views.RequestListView.as_view(), name='request_list'),
    path('requests/<int:control_number>/view/', view=views.RequestDetailView.as_view(), name='request_detail'),

    path('requests/material-request/<int:control_number>/', view=labtech_approval_views.approve_material_request, name='approve_material_request'),
    path('requests/lab_apparel/<int:control_number>/', view=labtech_approval_views.approve_lab_apparel_request, name='approve_lab_apparel_request'),
    path('requests/<int:control_number>/borrow', view=approval_views.LabTechLending, name='lending_request'),

    path('return/items/<int:control_number>/', views.return_items, name='return_items'),
    path('return/lab_apparel/<int:control_number>/', views.return_lab_apparel, name='return_lab_apparel'),

    path('liabilities/', views.search_liabilities, name='search_liabilities'),
    
    path('reports/', view=reports_views.report_selection, name='reports'),
    path('reports/material-usage/', view=reports_views.material_usage_report, name='material_usage_report'),
    path('reports/material_usage/export/', view=reports_views.export_material_usage_report, name='export_material_usage_report'),
    path('reports/requests/', view=reports_views.requests_report, name='requests_report'),
    path('reports/requests/export/', view=reports_views.requests_report_csv, name='requests_report_csv'),
    path('reports/liabilities/', view=reports_views.liabilities_report, name='liabilities_report'),
    path('reports/liabilities/export/', view=reports_views.liabilities_report_csv, name='liabilities_report_csv'),
]