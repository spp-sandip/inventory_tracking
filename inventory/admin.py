# inventory/admin.py

from django.contrib import admin
from .models import Material

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('material_code', 'batch_code', 'material_description', 'quantity', 'value', 'department', 'batch_date')
    search_fields = ('material_code', 'batch_code', 'material_description', 'department')
    list_filter = ('department', 'batch_date')
