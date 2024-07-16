from django.contrib import admin
from django.urls import include, path
from inventory import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inventory/', include('inventory.urls')),
    path('', views.home, name='home')
]
