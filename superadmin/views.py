from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from major_clients.models import FreightCompany
from end_customers.models import EndCustomer
from core.models import UserProfile

def saas_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user_profile or request.user_profile.user_type != UserProfile.UserType.SAAS_PROVIDER:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('admin:index')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@saas_admin_required
def dashboard(request):
    freight_companies = FreightCompany.objects.all()
    end_customers = EndCustomer.objects.all()
    
    context = {
        'freight_companies': freight_companies,
        'end_customers': end_customers,
        'total_companies': freight_companies.count(),
        'total_customers': end_customers.count(),
    }
    return render(request, 'superadmin/dashboard.html', context)

class FreightCompanyListView(ListView):
    model = FreightCompany
    template_name = 'superadmin/freight_company_list.html'
    context_object_name = 'freight_companies'

    def get_queryset(self):
        return FreightCompany.objects.all()

class FreightCompanyCreateView(CreateView):
    model = FreightCompany
    template_name = 'superadmin/freight_company_form.html'
    fields = ['name']
    success_url = reverse_lazy('saas_admin:freight_company_list')

    def form_valid(self, form):
        form.instance.saas_provider = self.request.user_profile.linked_company.saas_provider
        return super().form_valid(form)

@login_required
@saas_admin_required
def end_customers_by_company(request, company_id):
    company = get_object_or_404(FreightCompany, id=company_id)
    end_customers = company.end_customers.all()
    
    context = {
        'company': company,
        'end_customers': end_customers,
    }
    return render(request, 'superadmin/end_customers_by_company.html', context)
