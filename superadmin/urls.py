from django.urls import path
from . import views
from .admin import saas_admin_site

app_name = 'saas_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('companies/', views.FreightCompanyListView.as_view(), name='freight_company_list'),
    path('companies/create/', views.FreightCompanyCreateView.as_view(), name='freight_company_create'),
    path('companies/<int:company_id>/end-customers/', views.end_customers_by_company, name='end_customers_by_company'),
    path('admin/', saas_admin_site.urls),
] 