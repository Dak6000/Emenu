from django.conf import settings
from django.conf.urls.static import static
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
    path('structure/', views.list_structures, name='structure'),

    # URLs de profil utilisateur
    path('profile/', views.profile_view, name='profile'),
    path('profile_form', views.profile_update, name='profile-update'),
    path('change_password', views.change_password, name='password-change'),
    path('account_delete', views.account_delete, name='account-delete'),

    # URLs de gestion des structures
    path('structure_detail/<int:pk>/', views.structure_detail, name='structure-detail'),
    path('structure_form/<int:pk>/', views.structure_update, name='structure-update'),
    path('account_delete/<int:pk>/', views.structure_delete, name='structure-delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)