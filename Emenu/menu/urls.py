from django.urls import path
from . import views

urlpatterns = [
    # Plats
    path('plats/', views.plat_list, name='plat-list'),
    path('plats/nouveau/', views.plat_create, name='plat-create'),
    path('plats/<int:pk>/modifier/', views.plat_update, name='plat-update'),
    path('plats/<int:pk>/supprimer/', views.plat_delete, name='plat-delete'),

    # Menus
    path('menus/', views.menu_list, name='menus-list'),
    path('menus/nouveau/', views.menu_create, name='menus-create'),
    path('menus/<int:pk>/modifier/', views.menu_update, name='menus-update'),
    path('menus/<int:pk>/supprimer/', views.menu_delete, name='menus-delete'),

    # Avis
    path('plats/<int:plat_pk>/avis/nouveau/', views.avis_create, name='avis-create-plat'),
    path('menus/<int:menu_pk>/avis/nouveau/', views.avis_create, name='avis-create-menus'),
    path('avis/<int:pk>/supprimer/', views.avis_delete, name='avis-delete'),
]