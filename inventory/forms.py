# inventory/forms.py

from django import forms
from .models import Material
from django.contrib.auth.forms import AuthenticationForm

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'material_code', 'batch_code', 'storage_location', 'material_description',
            'quantity', 'unit_of_measure', 'value', 'department', 'batch_date',
            'party_name', 'remarks', 'date_of_clearing', 'person', 'batch_ageing',
            'material_broad_group_desc'
        ]

class UpdateQuantityForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['quantity', 'value']

class CustomAuthenticationForm(AuthenticationForm):
    pass
