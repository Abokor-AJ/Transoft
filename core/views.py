from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import Invitation, UserProfile, FreightCompany
from .forms import (
    FreightCompanyRegistrationForm, EndCustomerRegistrationForm,
    InviteFreightAdminForm, InviteEndCustomerAdminForm, InviteEndCustomerStaffForm,
    AcceptInvitationForm, SelectFreightCompaniesForm
)
from django.contrib.auth.models import User
from django.db.models import Q

@login_required
def register_freight_company(request):
    if not request.user.profile.user_type == UserProfile.UserType.SAAS_PROVIDER:
        messages.error(request, "Only SaaS providers can register freight companies.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = FreightCompanyRegistrationForm(request.POST)
        if form.is_valid():
            company = form.save()
            messages.success(request, f"Freight company {company.name} registered successfully.")
            return redirect('invite_freight_admin')
    else:
        form = FreightCompanyRegistrationForm()

    return render(request, 'core/register_freight_company.html', {'form': form})

@login_required
def invite_freight_admin(request):
    if not request.user.profile.user_type == UserProfile.UserType.SAAS_PROVIDER:
        messages.error(request, "Only SaaS providers can invite freight company admins.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = InviteFreightAdminForm(request.POST)
        if form.is_valid():
            invitation = Invitation.objects.create(
                email=form.cleaned_data['email'],
                invitation_type=Invitation.InvitationType.FREIGHT_ADMIN,
                invited_by=request.user,
                freight_company=form.cleaned_data['company']
            )
            
            # Send invitation email
            invitation_url = request.build_absolute_uri(
                reverse('accept_invitation', args=[invitation.token])
            )
            send_mail(
                'Invitation to Join Freight Company',
                f'You have been invited to join {invitation.freight_company.name} as an admin. '
                f'Click here to accept: {invitation_url}',
                settings.DEFAULT_FROM_EMAIL,
                [invitation.email],
                fail_silently=False,
            )
            messages.success(request, f"Invitation sent to {invitation.email}")
            return redirect('dashboard')
    else:
        form = InviteFreightAdminForm()

    return render(request, 'core/invite_freight_admin.html', {'form': form})

@login_required
def register_end_customer(request):
    if not request.user.profile.user_type == UserProfile.UserType.FREIGHT_ADMIN:
        messages.error(request, "Only freight company admins can register end customers.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = EndCustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save()
            customer.freight_companies.add(request.user.profile.linked_company)
            messages.success(request, f"End customer {customer.name} registered successfully.")
            return redirect('invite_end_customer_admin')
    else:
        form = EndCustomerRegistrationForm()

    return render(request, 'core/register_end_customer.html', {'form': form})

@login_required
def invite_end_customer_admin(request):
    if not request.user.profile.user_type == UserProfile.UserType.FREIGHT_ADMIN:
        messages.error(request, "Only freight company admins can invite end customer admins.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = InviteEndCustomerAdminForm(request.POST)
        if form.is_valid():
            invitation = Invitation.objects.create(
                email=form.cleaned_data['email'],
                invitation_type=Invitation.InvitationType.END_CUSTOMER_ADMIN,
                invited_by=request.user,
                end_customer=form.cleaned_data['customer']
            )
            
            # Send invitation email
            invitation_url = request.build_absolute_uri(
                reverse('accept_invitation', args=[invitation.token])
            )
            send_mail(
                'Invitation to Join End Customer',
                f'You have been invited to join {invitation.end_customer.name} as an admin. '
                f'Click here to accept: {invitation_url}',
                settings.DEFAULT_FROM_EMAIL,
                [invitation.email],
                fail_silently=False,
            )
            messages.success(request, f"Invitation sent to {invitation.email}")
            return redirect('dashboard')
    else:
        form = InviteEndCustomerAdminForm(
            initial={'customer': request.user.profile.linked_company.end_customers.first()}
        )

    return render(request, 'core/invite_end_customer_admin.html', {'form': form})

@login_required
def invite_end_customer_staff(request):
    if not request.user.profile.user_type == UserProfile.UserType.END_CUSTOMER_ADMIN:
        messages.error(request, "Only end customer admins can invite staff members.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = InviteEndCustomerStaffForm(request.POST)
        if form.is_valid():
            invitation = Invitation.objects.create(
                email=form.cleaned_data['email'],
                invitation_type=Invitation.InvitationType.END_CUSTOMER_STAFF,
                invited_by=request.user,
                end_customer=request.user.profile.linked_customer
            )
            
            # Send invitation email
            invitation_url = request.build_absolute_uri(
                reverse('accept_invitation', args=[invitation.token])
            )
            send_mail(
                'Invitation to Join End Customer',
                f'You have been invited to join {invitation.end_customer.name} as a staff member. '
                f'Click here to accept: {invitation_url}',
                settings.DEFAULT_FROM_EMAIL,
                [invitation.email],
                fail_silently=False,
            )
            messages.success(request, f"Invitation sent to {invitation.email}")
            return redirect('dashboard')
    else:
        form = InviteEndCustomerStaffForm()

    return render(request, 'core/invite_end_customer_staff.html', {'form': form})

def accept_invitation(request, token):
    invitation = get_object_or_404(Invitation, token=token)
    
    if invitation.is_expired():
        messages.error(request, "This invitation has expired.")
        return redirect('login')
    
    if invitation.accepted:
        messages.error(request, "This invitation has already been accepted.")
        return redirect('login')

    if request.method == 'POST':
        form = AcceptInvitationForm(request.POST, invitation=invitation)
        if form.is_valid():
            user = form.save()
            if invitation.accept(user):
                messages.success(request, "Account created successfully. You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Failed to accept invitation.")
    else:
        form = AcceptInvitationForm(invitation=invitation)

    return render(request, 'core/accept_invitation.html', {'form': form, 'invitation': invitation})

@login_required
def select_freight_companies(request):
    if not request.user.profile.user_type == UserProfile.UserType.END_CUSTOMER_ADMIN:
        messages.error(request, "Only end customer admins can select freight companies.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = SelectFreightCompaniesForm(request.POST)
        if form.is_valid():
            request.user.profile.linked_customer.freight_companies.set(
                form.cleaned_data['freight_companies']
            )
            messages.success(request, "Freight companies updated successfully.")
            return redirect('dashboard')
    else:
        form = SelectFreightCompaniesForm(initial={
            'freight_companies': request.user.profile.linked_customer.freight_companies.all()
        })

    return render(request, 'core/select_freight_companies.html', {'form': form})

@login_required
def switch_provider(request):
    if request.user.profile.user_type != UserProfile.UserType.END_CUSTOMER_ADMIN:
        messages.error(request, "Only end customer admins can switch providers.")
        return redirect('dashboard')

    if request.method == 'POST':
        provider_id = request.POST.get('provider_id')
        try:
            provider = FreightCompany.objects.get(
                id=provider_id,
                end_customers=request.user.profile.linked_customer
            )
            request.session['selected_provider'] = {
                'id': provider.id,
                'name': provider.name
            }
            messages.success(request, f"Switched to {provider.name}")
        except FreightCompany.DoesNotExist:
            messages.error(request, "Invalid provider selected.")
    
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def landing_page(request):
    if not hasattr(request, 'user_profile'):
        return redirect('admin:index')
        
    if request.user_profile.user_type == UserProfile.UserType.SAAS_PROVIDER:
        return redirect('saas_admin:dashboard')
    elif request.user_profile.user_type == UserProfile.UserType.FREIGHT_ADMIN:
        return redirect('freight_portal:dashboard')
    elif request.user_profile.user_type in [UserProfile.UserType.END_CUSTOMER_ADMIN, UserProfile.UserType.END_CUSTOMER_STAFF]:
        # For end customers, we need to get their linked customer
        if request.user_profile.linked_customer:
            return redirect('customer_portal:dashboard', customer_id=request.user_profile.linked_customer.id)
    
    # If no specific role or no linked customer, redirect to admin
    return redirect('admin:index')
