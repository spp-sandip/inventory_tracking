from django.shortcuts import render, redirect
from .models import Material
import qrcode
from django.shortcuts import get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from .forms import MaterialForm, UpdateQuantityForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import UpdateView
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm
from django.urls import reverse_lazy
from .utils import read_and_normalize_excel, column_mapping, expected_columns, map_columns
from django.utils.dateparse import parse_date
import pandas as pd

def home(request):
    return redirect('material_list')

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'

    def get_success_url(self):
        user_groups = self.request.user.groups.values_list('name', flat=True)
        department_redirect_urls = {
            'Tape & Loom': reverse_lazy('tape_loom_material_list'),
            'FIBC': reverse_lazy('fibc_material_list'),
            'Lamination': reverse_lazy('lamination_material_list'),
            'Coating 1': reverse_lazy('coating1_material_list'),
            'Coating 2': reverse_lazy('coating2_material_list'),
            'Film': reverse_lazy('film_material_list'),
            'Fabrication': reverse_lazy('fabrication_material_list'),
            'Oil & Liquid': reverse_lazy('oil_liquid_material_list'),
        }

        for group in user_groups:
            department = next((key for key in department_redirect_urls.keys() if key in group), None)
            if department:
                return department_redirect_urls[department]
        
        return reverse_lazy('material_list')

@login_required
def department_redirect(request):
    user_groups = request.user.groups.values_list('name', flat=True)
    
    department_redirect_urls = {
        'Tape & Loom': 'tape_loom_material_list',
        'FIBC': 'fibc_material_list',
        'Lamination': 'lamination_material_list',
        'Coating 1': 'coating1_material_list',
        'Coating 2': 'coating2_material_list',
        'Film': 'film_material_list',
        'Fabrication': 'fabrication_material_list',
        'Oil & Liquid': 'oil_liquid_material_list',
    }

    for group in user_groups:
        department = next((key for key in department_redirect_urls.keys() if key in group), None)
        if department:
            return redirect(department_redirect_urls[department])
    
    return redirect('material_list')

@login_required
def material_list(request):
    materials = Material.objects.all()
    context = {
        'materials': materials,
        'request': request,
    }
    return render(request, 'inventory/material_list.html', context)

def material_detail(request, material_code, batch_code):
    material = get_object_or_404(Material, material_code=material_code, batch_code=batch_code)
    context = {
        'material': material,
        'request': request,
    }
    return render(request, 'inventory/material_detail.html', context)

@login_required
@permission_required('inventory.add_material', raise_exception=True)
def add_material(request):
    user_groups = request.user.groups.values_list('name', flat=True)
    allowed_groups = [
        'Internal Audit', 'Operations', 'Plant Head',
        'Tape & Loom Production Engineer', 'Tape & Loom Stock Keeper',
        'FIBC Production Engineer', 'FIBC Stock Keeper',
        'Lamination Production Engineer', 'Lamination Stock Keeper',
        'Coating 1 Production Engineer', 'Coating 1 Stock Keeper',
        'Coating 2 Production Engineer', 'Coating 2 Stock Keeper',
        'Film Production Engineer', 'Film Stock Keeper',
        'Fabrication Production Engineer', 'Fabrication Stock Keeper',
        'Oil & Liquid Production Engineer', 'Oil & Liquid Stock Keeper'
    ]

    if not set(user_groups).intersection(allowed_groups):
        return HttpResponse("You do not have permission to add material.", status=403)

    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('material_list')
    else:
        form = MaterialForm()

    context = {
        'form': form,
        'user_groups': user_groups
    }
    return render(request, 'inventory/add_material.html', context)

@login_required
def generate_qr_code(request, material_code, batch_code):
    material = get_object_or_404(Material, material_code=material_code, batch_code=batch_code)
    url = request.build_absolute_uri(f'/inventory/materials/{material_code}/{batch_code}/')
    qr = qrcode.make(url)
    response = HttpResponse(content_type='image/png')
    qr.save(response, "PNG")
    return response

@login_required
def upload_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        print(f"Received Excel File: {excel_file.name}")
        df, missing_columns, extra_columns, missing_values_warnings = read_and_normalize_excel(excel_file, column_mapping, expected_columns)

        print(f"Original Columns: {df.columns}")
        df, missing_columns, extra_columns = map_columns(df, column_mapping, expected_columns)
        print(f"Renamed Columns: {df.columns}")

        print(f"Missing Columns: {missing_columns}")
        print(f"Extra Columns: {extra_columns}")
        print(f"Missing Values Warnings: {missing_values_warnings}")

        warnings = missing_values_warnings[:]
        for index, row in df.iterrows():
            #print(f"Processing Row {index}: {row}")
            material_code = row['material_code']
            batch_code = row['batch_code']
            storage_location = row['storage_location']

            if pd.isnull(material_code) or pd.isnull(batch_code):
                warnings.append(f"Skipping row {index+1} due to missing material_code or batch_code.")
                continue

            existing_material = Material.objects.filter(material_code=material_code, batch_code=batch_code, storage_location=storage_location).first()

            if existing_material:
                # Handle partial updates
                if row['quantity'] is not None:
                    existing_material.quantity = row['quantity']
                if row['value'] is not None:
                    existing_material.value = row['value']
                existing_material.save()
                warnings.append(f"Updated existing material: {material_code}, batch: {batch_code}")
            else:
                Material.objects.create(
                    material_code=row['material_code'],
                    batch_code=row['batch_code'],
                    storage_location=row['storage_location'],
                    material_description=row['material_description'] if row['material_description'] is not None else '',
                    quantity=row['quantity'] if row['quantity'] is not None else 0,
                    unit_of_measure=row['unit_of_measure'] if row['unit_of_measure'] is not None else '',
                    value=row['value'] if row['value'] is not None else 0,  # Default to 0 if None
                    department=row['department'] if row['department'] is not None else '',
                    batch_date=parse_date(str(row['batch_date'])) if row['batch_date'] else None,
                    party_name=row['party_name'] if row['party_name'] is not None else '',
                    remarks=row['remarks'] if row['remarks'] is not None else '',
                    date_of_clearing=parse_date(str(row['date_of_clearing'])) if row['date_of_clearing'] else None,
                    person=row['person'] if row['person'] is not None else '',
                    batch_ageing=row['batch_ageing'] if row['batch_ageing'] is not None else 0,
                    material_broad_group_desc=row['material_broad_group_desc'] if row['material_broad_group_desc'] is not None else ''
                )

        return render(request, 'inventory/upload_success.html', {
            'missing_columns': missing_columns, 
            'extra_columns': extra_columns,
            'warnings': warnings
        })

    return render(request, 'inventory/upload_excel.html')


@login_required
@permission_required('inventory.change_material', raise_exception=True)
def update_quantity(request, material_code=None, batch_code=None):
    if request.method == 'POST':
        form = UpdateQuantityForm(request.POST)
        if form.is_valid():
            material_code = form.cleaned_data['material_code']
            batch_code = form.cleaned_data['batch_code']
            quantity_used = form.cleaned_data['quantity_used']
            
            try:
                material = Material.objects.get(material_code=material_code, batch_code=batch_code)
                if material.quantity < quantity_used:
                    return HttpResponse("Not enough material available.", status=400)
                
                # Calculate the unit price
                unit_price = material.value / material.quantity if material.quantity > 0 else 0
                
                # Update quantity and value
                material.quantity -= quantity_used
                material.value = material.quantity * unit_price if material.value is not None else None
                material.save()
                return redirect('material_list')
            except Material.DoesNotExist:
                return HttpResponse("Material not found.", status=404)
    else:
        initial_data = {}
        if material_code and batch_code:
            try:
                material = Material.objects.get(material_code=material_code, batch_code=batch_code)
                initial_data = {
                    'material_code': material.material_code,
                    'batch_code': material.batch_code,
                    'quantity_used': 0  # Default to 0
                }
            except Material.DoesNotExist:
                return HttpResponse("Material not found.", status=404)
        form = UpdateQuantityForm(initial=initial_data)
    
    return render(request, 'inventory/update_quantity.html', {'form': form, 'material': material})

class MaterialUpdateView(PermissionRequiredMixin, UpdateView):
    model = Material
    fields = [
        'material_code', 'storage_location', 'batch_code', 'material_description',
        'quantity', 'department', 'batch_date', 'party_name', 'remarks',
        'date_of_clearing', 'person', 'batch_ageing', 'material_broad_group_desc'
    ]
    template_name = 'inventory/update_material.html'
    permission_required = 'inventory.change_material'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['read_only'] = ['value', 'con_factor', 'con_uom']
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        read_only_fields = ['value', 'con_factor', 'con_uom']
        for field in read_only_fields:
            form.fields[field].widget.attrs['readonly'] = True
        return form

@login_required
def tape_loom_material_list(request):
    materials = Material.objects.filter(department='Tape & Loom')
    return render(request, 'inventory/material_list.html', {'materials': materials})

@login_required
def fibc_material_list(request):
    materials = Material.objects.filter(department='FIBC')
    return render(request, 'inventory/material_list.html', {'materials': materials})

@login_required
def lamination_material_list(request):
    materials = Material.objects.filter(department='Lamination')
    return render(request, 'inventory/material_list.html', {'materials': materials})

@login_required
def coating1_material_list(request):
    materials = Material.objects.filter(department='Coating 1')
    return render(request, 'inventory/material_list.html', {'materials': materials})

@login_required
def coating2_material_list(request):
    materials = Material.objects.filter(department='Coating 2')
    return render(request, 'inventory/material_list.html', {'materials': materials})

@login_required
def film_material_list(request):
    materials = Material.objects.filter(department='Film')
    return render(request, 'inventory/material_list.html', {'materials': materials})

@login_required
def fabrication_material_list(request):
    materials = Material.objects.filter(department='Fabrication')
    return render(request, 'inventory/material_list.html', {'materials': materials})

@login_required
def oil_liquid_material_list(request):
    materials = Material.objects.filter(department='Oil & Liquid')
    return render(request, 'inventory/material_list.html', {'materials': materials})
