from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from .forms import UserLoginForm, UserRegistrationForm, StructureRegistrationForm
from .models import Structure, User, UserLoginHistory
from django.utils import timezone
from .forms import UserUpdateForm, CustomPasswordChangeForm, UserDeleteForm, StructureUpdateForm


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)

            if user is not None:
                # Vérifie si l'utilisateur était précédemment déconnecté
                if not request.user.is_authenticated:
                    # Enregistre seulement si c'est une nouvelle connexion
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

                    UserLoginHistory.objects.create(
                        user=user,
                        ip_address=ip_address,
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                        login_success=True
                    )

                login(request, user)
                messages.success(request, f"Bienvenue {user.first_name}!")

                # Vérifie si l'utilisateur a une structure associée
                if hasattr(user, 'structure'):
                    return redirect('accounts:dashboard')
                else:
                    return redirect('accounts:home')  # Remplacez 'home' par le nom de votre URL d'accueil

        # Gestion des échecs de connexion (identique)
        email = request.POST.get('username')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        UserLoginHistory.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            login_success=False
        )

        messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            messages.success(request, "Compte créé avec succès! Vous pouvez maintenant vous connecter.")
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register_user.html', {'form': form})


def register_structure(request):
    if request.method == 'POST':
        form = StructureRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            structure = form.save(commit=False)
            if request.user.is_authenticated:
                structure.user = request.user
                structure.save()
                messages.success(request, "Structure enregistrée avec succès!")
                return redirect('accounts:dashboard')
    else:
        form = StructureRegistrationForm()
    return render(request, 'accounts/register_structure.html', {'form': form})


@login_required
def dashboard(request):
    # Récupère les structures de l'utilisateur connecté
    structures = Structure.objects.filter(user=request.user)

    # Récupère l'historique des connexions (30 derniers jours)
    login_history = UserLoginHistory.objects.filter(
        user=request.user,
        login_time__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by('-login_time')

    context = {
        'structures': structures,
        'structures_count': structures.count(),
        'login_history': login_history,
    }
    return render(request, 'dashboard.html', context)


def home_view(request):
    context = {
        'categories': [
            {'name': 'Restaurants', 'icon': 'fa-utensils', 'count': 42},
            {'name': 'Cafés', 'icon': 'fa-coffee', 'count': 23},
            {'name': 'Hôtels', 'icon': 'fa-hotel', 'count': 15},
            {'name': 'Bars', 'icon': 'fa-glass-martini-alt', 'count': 18},
        ],
        'featured_structures': Structure.objects.all()[:4]  # Récupère les 4 premières structures
    }
    return render(request, 'Accueil.html', context)


def logout_view(request):
    if request.user.is_authenticated:
        # Enregistrer la déconnexion si besoin
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        UserLoginHistory.objects.create(
            user=request.user,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            login_success=True,  # Ou ajoutez un champ 'action' pour différencier connexion/déconnexion
            action='LOGOUT'  # Ajoutez ce champ à votre modèle si vous voulez tracker les déconnexions
        )

    logout(request)
    return redirect('accounts:login')




@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_update(request):
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
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def account_delete(request):
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
    # Récupérer toutes les structures (ou seulement les featured si vous voulez)
    featured_structures = Structure.objects.all().order_by('-id')  # ou .filter(featured=True)

    # Récupérer les villes et catégories uniques pour les filtres
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
    structure = get_object_or_404(Structure, pk=pk, user=request.user)
    return render(request, 'accounts/structure_detail.html', {'structure': structure})


@login_required
def structure_update(request, pk):
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
    structure = get_object_or_404(Structure, pk=pk, user=request.user)
    if request.method == 'POST':
        structure.delete()
        messages.success(request, 'La structure a été supprimée avec succès!')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/confirm_delete.html', {'object': structure})