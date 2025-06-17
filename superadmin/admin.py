from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils.html import format_html
from major_clients.models import FreightCompany
from end_customers.models import EndCustomer
from core.models import UserProfile

class FreightCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'end_customers_count', 'view_end_customers')
    search_fields = ('name',)

    def end_customers_count(self, obj):
        return obj.end_customers.count()
    end_customers_count.short_description = 'End Customers'

    def view_end_customers(self, obj):
        url = reverse('saas_admin:end_customers_by_company', args=[obj.id])
        return format_html('<a href="{}">View End Customers</a>', url)
    view_end_customers.short_description = 'End Customers'

class EndCustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'freight_companies_list')
    search_fields = ('name',)
    filter_horizontal = ('freight_companies',)

    def freight_companies_list(self, obj):
        return ", ".join([company.name for company in obj.freight_companies.all()])
    freight_companies_list.short_description = 'Freight Companies'

class SaasAdminSite(AdminSite):
    site_header = 'Freight SaaS Administration'
    site_title = 'Freight SaaS Admin Portal'
    index_title = 'Welcome to Freight SaaS Admin Portal'

saas_admin_site = SaasAdminSite(name='saas_admin')

# Register models with the custom admin site
saas_admin_site.register(FreightCompany, FreightCompanyAdmin)
saas_admin_site.register(EndCustomer, EndCustomerAdmin)
