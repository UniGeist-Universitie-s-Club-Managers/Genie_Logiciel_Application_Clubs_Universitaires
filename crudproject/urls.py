from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirige la racine vers le dashboard
    path('', lambda request: redirect('dashboard')),

    # Auth/User management
    path('accounts/', include('accounts.urls')),
]
