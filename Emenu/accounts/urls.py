from django.urls import path
from . import views  # Importez vos vues depuis accounts/views.py

app_name = 'accounts'  # Namespace pour les URLs

urlpatterns = [
    # Page d'accueil (racine du site)
    path('', views.home_view, name='home'),

    # Authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_user, name='register'),
    path('register_structure/', views.register_structure, name='register_structure'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]