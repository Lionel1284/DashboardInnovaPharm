from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/', views.list_users, name='list_users'),
    path('users/<str:rut>/edit/', views.edit_user, name='edit_user'),
    path('users/<str:rut>/toggle/<str:action>/', views.toggle_user_status, name='toggle_user_status'),
]