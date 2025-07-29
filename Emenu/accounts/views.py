from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserLoginForm, UserRegistrationForm, StructureRegistrationForm
from .models import Structure

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {user.first_name}!")
                return redirect('accounts:dashboard')  # Redirige vers la page d'accueil après connexion
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

    context = {
        'structures': structures,
        'structures_count': structures.count(),
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
    logout(request)  # Déconnecte l'utilisateur
    return redirect('accounts:login')  # Redirige vers la page de connexion