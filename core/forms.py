from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Invitation, FreightCompany, EndCustomer

class FreightCompanyRegistrationForm(forms.ModelForm):
    class Meta:
        model = FreightCompany
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class EndCustomerRegistrationForm(forms.ModelForm):
    class Meta:
        model = EndCustomer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class InviteFreightAdminForm(forms.Form):
    email = forms.EmailField()
    company = forms.ModelChoiceField(queryset=FreightCompany.objects.all())

class InviteEndCustomerAdminForm(forms.Form):
    email = forms.EmailField()
    customer = forms.ModelChoiceField(queryset=EndCustomer.objects.all())

class InviteEndCustomerStaffForm(forms.Form):
    email = forms.EmailField()
    customer = forms.ModelChoiceField(queryset=EndCustomer.objects.all())

class AcceptInvitationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        self.invitation = kwargs.pop('invitation', None)
        super().__init__(*args, **kwargs)
        if self.invitation:
            self.fields['email'].initial = self.invitation.email
            self.fields['email'].widget.attrs['readonly'] = True

class SelectFreightCompaniesForm(forms.Form):
    freight_companies = forms.ModelMultipleChoiceField(
        queryset=FreightCompany.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    ) 