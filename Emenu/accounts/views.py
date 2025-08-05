# Importations des modules nécessaires
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages

from menu.models import Menu
from .forms import UserLoginForm, UserRegistrationForm, StructureRegistrationForm
from .models import Structure, User, UserLoginHistory
from django.utils import timezone
from .forms import UserUpdateForm, CustomPasswordChangeForm, UserDeleteForm, StructureUpdateForm
from django.contrib.auth import get_user_model

# Récupère le modèle User personnalisé (si vous avez un modèle User personnalisé)
User = get_user_model()

def login_view(request):
    # Si l'utilisateur est déjà authentifié, on le redirige
    if request.user.is_authenticated:
        # Vérifie si l'utilisateur a une structure associée
        if hasattr(request.user, 'structure') and request.user.structure:
            return redirect('accounts:dashboard')
        return redirect('accounts:home')

    if request.method == 'POST':
        # Traitement du formulaire de connexion
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # On utilise l'email comme identifiant
            password = form.cleaned_data.get('password')

            # Authentification de l'utilisateur
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Enregistrement de la tentative de connexion réussie dans l'historique
                # Récupération de l'adresse IP (gère les proxies)
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

                # Création d'un enregistrement d'historique de connexion
                UserLoginHistory.objects.create(
                    user=user,
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],  # Limité à 255 caractères
                    login_success=True
                )

                # Connexion effective de l'utilisateur
                login(request, user)
                messages.success(request, f"Bienvenue {user.first_name}!")

                # Redirection selon si l'utilisateur a une structure associée
                if Structure.objects.filter(user=user).exists():
                    return redirect('accounts:dashboard')
                return redirect('accounts:home')

        # Gestion des échecs de connexion
        email = request.POST.get('username', '')
        try:
            user = User.objects.get(email=email) if email else None
        except User.DoesNotExist:
            user = None

        if user:
            # Enregistrement de la tentative de connexion échouée
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

            UserLoginHistory.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                login_success=False
            )

        messages.error(request, "Email ou mot de passe incorrect.")
        return redirect('accounts:login')

    else:
        # Affichage du formulaire vide pour une requête GET
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def register_user(request):
    """Vue pour l'inscription d'un nouvel utilisateur"""
    if request.method == 'POST':
        # Traitement du formulaire d'inscription
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email  # On utilise l'email comme nom d'utilisateur
            user.save()
            messages.success(request, "Compte créé avec succès! Vous pouvez maintenant vous connecter.")
            return redirect('accounts:login')
    else:
        # Affichage du formulaire vide pour une requête GET
        form = UserRegistrationForm()
    return render(request, 'accounts/register_user.html', {'form': form})

@login_required
def register_structure(request):
    """Vue pour enregistrer une nouvelle structure (réservée aux utilisateurs connectés)"""
    if request.method == 'POST':
        form = StructureRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            structure = form.save(commit=False)
            structure.user = request.user  # Associe la structure à l'utilisateur connecté

            try:
                structure.save()
                messages.success(request, f"La structure {structure.nom} a été créée avec succès!")
                # Redirection vers la page précédente ou le dashboard
                return redirect('accounts:dashboard')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = StructureRegistrationForm()

    return render(request, 'accounts/register_structure.html', {
        'form': form,
        'structures_count': request.user.structure.count()  # Compte le nombre de structures de l'utilisateur
    })

@login_required
def dashboard(request):
    """Tableau de bord de l'utilisateur connecté"""
    # Récupère les structures de l'utilisateur
    structures = Structure.objects.filter(user=request.user)

    # Récupère l'historique des connexions des 10 derniers jours
    login_history = UserLoginHistory.objects.filter(
        user=request.user,
        login_time__gte=timezone.now() - timezone.timedelta(days=10)
    ).order_by('-login_time')

    context = {
        'structures': structures,
        'structures_count': structures.count(),
        'login_history': login_history,
    }
    return render(request, 'dashboard.html', context)

def home_view(request):
    """Page d'accueil du site"""
    context = {
        'categories': [
            {'name': 'Restaurants', 'icon': 'fa-utensils', 'count': 42},
            {'name': 'Cafés', 'icon': 'fa-coffee', 'count': 23},
            {'name': 'Hôtels', 'icon': 'fa-hotel', 'count': 15},
            {'name': 'Bars', 'icon': 'fa-glass-martini-alt', 'count': 18},
        ],
        'featured_structures': Structure.objects.all()[:4]  # 4 premières structures
    }
    return render(request, 'index.html', context)

@login_required
def logout_view(request):
    """Déconnexion de l'utilisateur"""
    if request.user.is_authenticated:
        # Enregistrement de la déconnexion dans l'historique
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        UserLoginHistory.objects.create(
            user=request.user,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            login_success=True,
            action='LOGOUT'  # Champ optionnel pour différencier connexion/déconnexion
        )

    logout(request)
    return redirect('accounts:login')

@login_required
def profile_view(request):
    """Affichage du profil utilisateur"""
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_update(request):
    """Mise à jour du profil utilisateur"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/profile_form.html', {'form': form})

@login_required
def change_password(request):
    """Changement de mot de passe"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Met à jour la session pour ne pas déconnecter l'utilisateur
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def account_delete(request):
    """Suppression du compte utilisateur"""
    if request.method == 'POST':
        form = UserDeleteForm(request.POST)
        if form.is_valid():
            request.user.delete()
            logout(request)
            messages.success(request, 'Votre compte a été supprimé avec succès.')
            return redirect('accounts:home')
    else:
        form = UserDeleteForm()

    return render(request, 'accounts/account_delete.html', {'form': form})

def list_structures(request):
    """Liste toutes les structures disponibles"""
    featured_structures = Structure.objects.all().order_by('-id')

    # Récupère les villes et catégories uniques pour les filtres
    villes = Structure.objects.values_list('ville', flat=True).distinct()
    categories = Structure.objects.values_list('type', flat=True).distinct()

    context = {
        'featured_structures': featured_structures,
        'villes': villes,
        'categories': categories,
        'title': 'Nos Structures Partenaires'
    }
    return render(request, 'structure.html', context)

@login_required
def structure_detail(request, pk):
    """Détails d'une structure spécifique (accessible seulement par son propriétaire)"""
    structure = get_object_or_404(Structure, pk=pk, user=request.user)
    return render(request, 'accounts/structure_detail.html', {'structure': structure})

@login_required(login_url='accounts:login')
def detail(request, pk):
    """Détails d'une structure spécifique avec les menus et les plats qui la constituent"""
    structure = get_object_or_404(Structure, pk=pk)
    menus = Menu.objects.filter(structure=structure).prefetch_related(
        'plats')  # Récupère tous les menus de cette structure avec leurs plats

    context = {
        'structure': structure,
        'menus': menus,
        'has_structure': request.user == structure.user  # Vérifie si l'utilisateur est propriétaire
    }
    return render(request, 'detail.html', context)

@login_required
def structure_update(request, pk):
    """Mise à jour d'une structure (accessible seulement par son propriétaire)"""
    structure = get_object_or_404(Structure, pk=pk, user=request.user)
    if request.method == 'POST':
        form = StructureUpdateForm(request.POST, request.FILES, instance=structure)
        if form.is_valid():
            form.save()
            messages.success(request, 'La structure a été mise à jour avec succès!')
            return redirect('accounts:structure-detail', pk=structure.pk)
    else:
        form = StructureUpdateForm(instance=structure)

    return render(request, 'accounts/structure_form.html', {'form': form, 'structure': structure})

@login_required
def structure_delete(request, pk):
    """Suppression d'une structure (accessible seulement par son propriétaire)"""
    structure = get_object_or_404(Structure, pk=pk, user=request.user)
    if request.method == 'POST':
        structure.delete()
        messages.success(request, 'La structure a été supprimée avec succès!')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/confirm_delete.html', {'object': structure})