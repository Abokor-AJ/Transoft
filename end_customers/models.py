from django.db import models
from major_clients.models import FreightCompany

class EndCustomer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    freight_companies = models.ManyToManyField(
        FreightCompany,
        related_name='freight_companies'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "End Customer"
        verbose_name_plural = "End Customers"
