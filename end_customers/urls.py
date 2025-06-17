from django.urls import path
from . import views

app_name = 'customer_portal'

urlpatterns = [
    path('<int:customer_id>/', views.portal_dashboard, name='dashboard'),
    path('<int:customer_id>/company/<int:company_id>/', views.freight_company_view, name='freight_company_view'),
    path('<int:customer_id>/staff/', views.manage_staff, name='manage_staff'),
] 