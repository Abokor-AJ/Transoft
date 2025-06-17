from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.db.models import Q
from .models import FreightCompany
from end_customers.models import EndCustomer
from core.models import UserProfile

def freight_admin_required(view_func):
    def wrapper(request, company_id, *args, **kwargs):
        if not request.user_profile:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('admin:index')
            
        # Allow superadmin access
        if request.user_profile.user_type == UserProfile.UserType.SAAS_PROVIDER:
            company = get_object_or_404(FreightCompany, id=company_id)
            return view_func(request, company_id, *args, **kwargs)
            
        # Check freight admin permissions
        if request.user_profile.user_type != UserProfile.UserType.FREIGHT_ADMIN:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('admin:index')
        
        company = get_object_or_404(FreightCompany, id=company_id)
        if request.user_profile.linked_company != company:
            messages.error(request, "You can only access your own company's portal.")
            return redirect('admin:index')
            
        return view_func(request, company_id, *args, **kwargs)
    return wrapper

@login_required
@freight_admin_required
def portal_dashboard(request, company_id):
    company = get_object_or_404(FreightCompany, id=company_id)
    end_customers = company.end_customers.all()
    staff_users = UserProfile.objects.filter(
        user_type=UserProfile.UserType.FREIGHT_ADMIN,
        linked_company=company
    )
    
    context = {
        'company': company,
        'end_customers': end_customers,
        'staff_users': staff_users,
        'total_customers': end_customers.count(),
        'total_staff': staff_users.count(),
    }
    return render(request, 'major_clients/portal_dashboard.html', context)

@login_required
@freight_admin_required
def manage_end_customers(request, company_id):
    company = get_object_or_404(FreightCompany, id=company_id)
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        action = request.POST.get('action')
        
        if action == 'add':
            customer = get_object_or_404(EndCustomer, id=customer_id)
            company.end_customers.add(customer)
            messages.success(request, f'Added {customer.name} to your customers.')
        elif action == 'remove':
            customer = get_object_or_404(EndCustomer, id=customer_id)
            company.end_customers.remove(customer)
            messages.success(request, f'Removed {customer.name} from your customers.')
    
    current_customers = company.end_customers.all()
    available_customers = EndCustomer.objects.exclude(id__in=current_customers)
    
    context = {
        'company': company,
        'current_customers': current_customers,
        'available_customers': available_customers,
    }
    return render(request, 'major_clients/manage_end_customers.html', context)

@login_required
@freight_admin_required
def manage_staff(request, company_id):
    company = get_object_or_404(FreightCompany, id=company_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        if action == 'add':
            user = get_object_or_404(User, id=user_id)
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'user_type': UserProfile.UserType.FREIGHT_ADMIN,
                    'linked_company': company
                }
            )
            if not created:
                profile.user_type = UserProfile.UserType.FREIGHT_ADMIN
                profile.linked_company = company
                profile.save()
            messages.success(request, f'Added {user.username} to your staff.')
        elif action == 'remove':
            profile = get_object_or_404(UserProfile, user_id=user_id, linked_company=company)
            profile.delete()
            messages.success(request, f'Removed staff member.')
    
    staff_profiles = UserProfile.objects.filter(
        user_type=UserProfile.UserType.FREIGHT_ADMIN,
        linked_company=company
    )
    available_users = User.objects.exclude(
        id__in=staff_profiles.values_list('user_id', flat=True)
    )
    
    context = {
        'company': company,
        'staff_profiles': staff_profiles,
        'available_users': available_users,
    }
    return render(request, 'major_clients/manage_staff.html', context)
