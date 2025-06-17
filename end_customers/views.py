from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.models import User
from .models import EndCustomer
from major_clients.models import FreightCompany
from core.models import UserProfile

def customer_admin_required(view_func):
    def wrapper(request, customer_id, *args, **kwargs):
        if not request.user_profile:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('admin:index')
            
        # Allow superadmin access
        if request.user_profile.user_type == UserProfile.UserType.SAAS_PROVIDER:
            customer = get_object_or_404(EndCustomer, id=customer_id)
            return view_func(request, customer_id, *args, **kwargs)
            
        # Check end customer admin permissions
        if request.user_profile.user_type != UserProfile.UserType.END_CUSTOMER_ADMIN:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('admin:index')
        
        customer = get_object_or_404(EndCustomer, id=customer_id)
        if request.user_profile.linked_customer != customer:
            messages.error(request, "You can only access your own customer portal.")
            return redirect('admin:index')
            
        return view_func(request, customer_id, *args, **kwargs)
    return wrapper

@login_required
@customer_admin_required
def portal_dashboard(request, customer_id):
    customer = get_object_or_404(EndCustomer, id=customer_id)
    freight_companies = customer.freight_companies.all()
    staff_users = UserProfile.objects.filter(
        user_type=UserProfile.UserType.END_CUSTOMER_ADMIN,
        linked_customer=customer
    )
    
    context = {
        'customer': customer,
        'freight_companies': freight_companies,
        'staff_users': staff_users,
        'total_companies': freight_companies.count(),
        'total_staff': staff_users.count(),
    }
    return render(request, 'end_customers/portal_dashboard.html', context)

@login_required
@customer_admin_required
def freight_company_view(request, customer_id, company_id):
    customer = get_object_or_404(EndCustomer, id=customer_id)
    company = get_object_or_404(FreightCompany, id=company_id)
    
    # Verify the company is associated with this customer
    if company not in customer.freight_companies.all():
        messages.error(request, "This freight company is not associated with your customer account.")
        return redirect('customer_portal:dashboard', customer_id=customer_id)
    
    context = {
        'customer': customer,
        'company': company,
        'all_companies': customer.freight_companies.all(),
    }
    return render(request, 'end_customers/freight_company_view.html', context)

@login_required
@customer_admin_required
def manage_staff(request, customer_id):
    customer = get_object_or_404(EndCustomer, id=customer_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        if action == 'add':
            user = get_object_or_404(User, id=user_id)
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'user_type': UserProfile.UserType.END_CUSTOMER_ADMIN,
                    'linked_customer': customer
                }
            )
            if not created:
                profile.user_type = UserProfile.UserType.END_CUSTOMER_ADMIN
                profile.linked_customer = customer
                profile.save()
            messages.success(request, f'Added {user.username} to your staff.')
        elif action == 'remove':
            profile = get_object_or_404(UserProfile, user_id=user_id, linked_customer=customer)
            profile.delete()
            messages.success(request, f'Removed staff member.')
    
    staff_profiles = UserProfile.objects.filter(
        user_type=UserProfile.UserType.END_CUSTOMER_ADMIN,
        linked_customer=customer
    )
    available_users = User.objects.exclude(
        id__in=staff_profiles.values_list('user_id', flat=True)
    )
    
    context = {
        'customer': customer,
        'staff_profiles': staff_profiles,
        'available_users': available_users,
    }
    return render(request, 'end_customers/manage_staff.html', context)
