from django.db import models

# Create your models here.

class SaaSProvider(models.Model):
    name = models.CharField(max_length=100)
    contact_email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "SaaS Provider"
        verbose_name_plural = "SaaS Providers"
