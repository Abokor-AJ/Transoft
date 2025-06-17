from django.urls import path
from . import views

app_name = 'freight_portal'

urlpatterns = [
    path('<int:company_id>/', views.portal_dashboard, name='dashboard'),
    path('<int:company_id>/end-customers/', views.manage_end_customers, name='manage_end_customers'),
    path('<int:company_id>/staff/', views.manage_staff, name='manage_staff'),
] 