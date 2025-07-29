from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),  # Inclut les URLs de l'app accounts à la racine
    # OU si vous voulez un préfixe :
    # path('accounts/', include('accounts.urls')),
]