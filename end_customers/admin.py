from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import EndCustomer

@admin.register(EndCustomer)
class EndCustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'portal_link')
    
    def portal_link(self, obj):
        url = reverse('customer_portal:dashboard', args=[obj.id])
        return format_html('<a href="{}" target="_blank">View Portal</a>', url)
    portal_link.short_description = 'Portal'
