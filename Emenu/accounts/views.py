from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserLoginForm, UserRegistrationForm, StructureRegistrationForm
from .models import Structure, User, UserLoginHistory
from django.utils import timezone


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
                return redirect('accounts:dashboard')

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
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email  # Pour compatibilité avec Django
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
    return render(request, 'home.html', context)


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
