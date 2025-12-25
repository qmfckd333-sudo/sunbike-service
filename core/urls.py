from django.urls import path
from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("customers/new/", views.CustomerCreateView.as_view(), name="customer_new"),
    path("vehicles/new/", views.VehicleCreateView.as_view(), name="vehicle_new"),
    path("workorders/new/", views.WorkOrderCreateView.as_view(), name="workorder_new"),
    path("workorders/<int:pk>/", views.WorkOrderDetailView.as_view(), name="workorder_detail"),
    path("workorders/<int:pk>/parts/add/", views.add_part, name="add_part"),
    path("workorders/<int:pk>/labor/add/", views.add_labor, name="add_labor"),
    path("workorders/<int:pk>/payments/add/", views.add_payment, name="add_payment"),
    path("workorders/<int:pk>/invoice.pdf", views.invoice_pdf, name="invoice_pdf"),
    path("workorders/<int:pk>/status/<str:action>/", views.workorder_status, name="workorder_status"),
]
