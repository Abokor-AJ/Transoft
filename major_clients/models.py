from django.db import models
from superadmin.models import SaaSProvider

# Create your models here.

class FreightCompany(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    end_customers = models.ManyToManyField('end_customers.EndCustomer', related_name='+')
    saas_provider = models.ForeignKey(
        SaaSProvider,
        on_delete=models.CASCADE,
        related_name='freight_companies'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Freight Company"
        verbose_name_plural = "Freight Companies"
