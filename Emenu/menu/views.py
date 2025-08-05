from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Plat, Menu, Avis
from .forms import PlatForm, MenuForm, AvisForm
from django.contrib.auth import get_user_model

User = get_user_model()

# CRUD pour Plat
@login_required
def plat_list(request):
    plats = Plat.objects.filter(createur=request.user)
    return render(request, 'plats/list.html', {'plats': plats})


@login_required
def plat_create(request):
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES)
        if form.is_valid():
            plat = form.save(commit=False)
            plat.createur = request.user
            plat.save()
            messages.success(request, 'Plat créé avec succès!')
            return redirect('plat-list')
    else:
        form = PlatForm()
    return render(request, 'plats/form.html', {'form': form, 'title': 'Créer un plat'})


@login_required
def plat_update(request, pk):
    plat = get_object_or_404(Plat, pk=pk, createur=request.user)
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES, instance=plat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plat mis à jour avec succès!')
            return redirect('plat-list')
    else:
        form = PlatForm(instance=plat)
    return render(request, 'plats/form.html', {'form': form, 'title': 'Modifier le plat'})


@login_required
def plat_delete(request, pk):
    plat = get_object_or_404(Plat, pk=pk, createur=request.user)
    if request.method == 'POST':
        plat.delete()
        messages.success(request, 'Plat supprimé avec succès!')
        return redirect('plat-list')
    return render(request, 'plats/confirm_delete.html', {'object': plat})


# CRUD pour Menu
@login_required
def menu_list(request):
    menus = Menu.objects.filter(createur=request.user)
    return render(request, 'menus/list.html', {'menus': menus})


@login_required
def menu_create(request):
    if request.method == 'POST':
        form = MenuForm(request.POST, user=request.user)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.createur = request.user
            # Associer automatiquement à la structure de l'utilisateur
            menu.structure = request.user.structure.first()
            menu.save()
            form.save_m2m()  # Pour sauvegarder les relations many-to-many
            messages.success(request, 'Menu créé avec succès!')
            return redirect('menus-list')
    else:
        form = MenuForm(user=request.user)

    return render(request, 'menus/form.html', {
        'form': form,
        'title': 'Créer un menu'
    })

@login_required
def menu_update(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu, user=request.user)
        if form.is_valid():
            menu = form.save()  # Sauvegarde l'instance principale
            messages.success(request, 'Le menu a été mis à jour avec succès.')
            return redirect('menus-list')
    else:
        form = MenuForm(instance=menu, user=request.user)

    return render(request, 'menus/form.html', {'form': form, 'title': 'Modifier un menu'})

@login_required
def menu_delete(request, pk):
    menu = get_object_or_404(Menu, pk=pk, createur=request.user)
    if request.method == 'POST':
        menu.delete()
        messages.success(request, 'Menu supprimé avec succès!')
        return redirect('menus-list')
    return render(request, 'menus/confirm_delete.html', {'object': menu})


# CRUD pour Avis
@login_required
def avis_create(request, plat_pk=None, menu_pk=None):
    plat = get_object_or_404(Plat, pk=plat_pk) if plat_pk else None
    menu = get_object_or_404(Menu, pk=menu_pk) if menu_pk else None

    if request.method == 'POST':
        form = AvisForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.auteur = request.user
            avis.plat = plat
            avis.menu = menu
            avis.save()
            messages.success(request, 'Avis publié avec succès!')
            return redirect(plat.get_absolute_url() if plat else menu.get_absolute_url())
    else:
        form = AvisForm()

    context = {
        'form': form,
        'plat': plat,
        'menus': menu,
        'title': 'Donner votre avis'
    }
    return render(request, 'avis/form.html', context)


@login_required
def avis_delete(request, pk):
    avis = get_object_or_404(Avis, pk=pk, auteur=request.user)
    if request.method == 'POST':
        avis.delete()
        messages.success(request, 'Avis supprimé avec succès!')
        return redirect('home')
    return render(request, 'avis/confirm_delete.html', {'object': avis})