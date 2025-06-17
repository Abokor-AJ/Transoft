from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from major_clients.models import FreightCompany
from end_customers.models import EndCustomer
import uuid
from django.utils import timezone
from datetime import timedelta


class UserProfile(models.Model):
    class UserType(models.TextChoices):
        SAAS_PROVIDER = 'SAAS_PROVIDER', 'SaaS Provider'
        FREIGHT_ADMIN = 'FREIGHT_ADMIN', 'Freight Company Admin'
        END_CUSTOMER_ADMIN = 'END_CUSTOMER_ADMIN', 'End Customer Admin'
        END_CUSTOMER_STAFF = 'END_CUSTOMER_STAFF', 'End Customer Staff'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.END_CUSTOMER_ADMIN
    )
    linked_company = models.ForeignKey(
        FreightCompany,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_profiles'
    )
    linked_customer = models.ForeignKey(
        EndCustomer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_profiles'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class DataScope(models.Model):
    freight_company = models.ForeignKey(
        FreightCompany,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='scoped_data'
    )
    end_customer = models.ForeignKey(
        EndCustomer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='scoped_data'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['freight_company']),
            models.Index(fields=['end_customer']),
        ]

class ScopedModelManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        request = getattr(self.model, '_request', None)
        
        if not request or not hasattr(request, 'user_profile'):
            return qs

        user_profile = request.user_profile
        
        if user_profile.user_type == UserProfile.UserType.SAAS_PROVIDER:
            return qs
        
        if user_profile.user_type == UserProfile.UserType.FREIGHT_ADMIN:
            return qs.filter(
                models.Q(datascope__freight_company=user_profile.linked_company) |
                models.Q(datascope__end_customer__in=user_profile.linked_company.end_customers.all())
            )
        
        if user_profile.user_type == UserProfile.UserType.END_CUSTOMER_ADMIN:
            return qs.filter(datascope__end_customer=user_profile.linked_customer)
        
        return qs.none()

class ScopedModel(models.Model):
    class Meta:
        abstract = True

    objects = ScopedModelManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        request = getattr(self, '_request', None)
        
        if request and hasattr(request, 'user_profile'):
            user_profile = request.user_profile
            DataScope.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.id,
                defaults={
                    'freight_company': user_profile.linked_company,
                    'end_customer': user_profile.linked_customer
                }
            )

class Invitation(models.Model):
    class InvitationType(models.TextChoices):
        FREIGHT_ADMIN = 'FREIGHT_ADMIN', 'Freight Company Admin'
        END_CUSTOMER_ADMIN = 'END_CUSTOMER_ADMIN', 'End Customer Admin'
        END_CUSTOMER_STAFF = 'END_CUSTOMER_STAFF', 'End Customer Staff'

    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    invitation_type = models.CharField(max_length=20, choices=InvitationType.choices)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_invitations')
    freight_company = models.ForeignKey(FreightCompany, on_delete=models.CASCADE, null=True, blank=True)
    end_customer = models.ForeignKey(EndCustomer, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def accept(self, user):
        if not self.is_expired() and not self.accepted:
            self.accepted = True
            self.accepted_at = timezone.now()
            self.save()

            # Create user profile based on invitation type
            profile = UserProfile.objects.create(
                user=user,
                user_type=self.invitation_type
            )

            if self.invitation_type == self.InvitationType.FREIGHT_ADMIN:
                profile.linked_company = self.freight_company
            elif self.invitation_type in [self.InvitationType.END_CUSTOMER_ADMIN, self.InvitationType.END_CUSTOMER_STAFF]:
                profile.linked_customer = self.end_customer

            profile.save()
            return True
        return False

    def __str__(self):
        return f"Invitation for {self.email} ({self.invitation_type})"
