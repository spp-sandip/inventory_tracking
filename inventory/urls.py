# inventory/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.material_list, name='material_list'),
    path('materials/', views.material_list, name='material_list'),
    path('materials/<str:material_code>/<str:batch_code>/', views.material_detail, name='material_detail'),
    path('materials/<str:material_code>/<str:batch_code>/qr/', views.generate_qr_code, name='generate_qr_code'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('add_material/', views.add_material, name='add_material'),
    path('update_quantity/<str:material_code>/<str:batch_code>/', views.update_quantity, name='update_quantity'),
    path('update_material/<int:pk>/', views.MaterialUpdateView.as_view(), name='update_material'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('department_redirect/', views.department_redirect, name='department_redirect'),
    #path('register/', views.register, name='register'),  # If you are using the custom registration

    # Department-specific material list URLs
    path('tape_loom/', views.tape_loom_material_list, name='tape_loom_material_list'),
    path('fibc/', views.fibc_material_list, name='fibc_material_list'),
    path('lamination/', views.lamination_material_list, name='lamination_material_list'),
    path('coating1/', views.coating1_material_list, name='coating1_material_list'),
    path('coating2/', views.coating2_material_list, name='coating2_material_list'),
    path('film/', views.film_material_list, name='film_material_list'),
    path('fabrication/', views.fabrication_material_list, name='fabrication_material_list'),
    path('oil_liquid/', views.oil_liquid_material_list, name='oil_liquid_material_list'),
]

