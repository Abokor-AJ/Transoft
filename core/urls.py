from django.urls import path
from . import views

urlpatterns = [
    path('register/freight-company/', views.register_freight_company, name='register_freight_company'),
    path('invite/freight-admin/', views.invite_freight_admin, name='invite_freight_admin'),
    path('register/end-customer/', views.register_end_customer, name='register_end_customer'),
    path('invite/end-customer-admin/', views.invite_end_customer_admin, name='invite_end_customer_admin'),
    path('invite/end-customer-staff/', views.invite_end_customer_staff, name='invite_end_customer_staff'),
    path('invitation/<uuid:token>/', views.accept_invitation, name='accept_invitation'),
    path('select-freight-companies/', views.select_freight_companies, name='select_freight_companies'),
    path('switch-provider/', views.switch_provider, name='switch_provider'),
] 