from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from admin_panel import views as admin_views

urlpatterns = [
    # URL para el admin de Django (opcional)
    path('django-admin/', admin.site.urls),
    
    # URLs de tu panel administrativo
    path('', include('admin_panel.urls')),
    
    # URLs de autenticación (si necesitas reset de contraseñas)
    path('reset-password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]