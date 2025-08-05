from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import Structure


class Plat(models.Model):
    CATEGORIES = (
        ('entree', 'Entrée'),
        ('plat', 'Plat principal'),
        ('dessert', 'Dessert'),
        ('boisson', 'Boisson'),
    )

    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    disponibilite = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='plats/', null=True, blank=True)
    createur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom


class Menu(models.Model):
    STATUS_CHOICES = (
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('brouillon', 'Brouillon'),
    )

    nom = models.CharField(max_length=100)
    date_creation = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon')
    plats = models.ManyToManyField('Plat', related_name='menus')
    createur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='menus')

    def __str__(self):
        return self.nom


class Avis(models.Model):
    NOTE_CHOICES = [
        (1, '1 - Très mauvais'),
        (2, '2 - Mauvais'),
        (3, '3 - Moyen'),
        (4, '4 - Bon'),
        (5, '5 - Excellent'),
    ]

    note = models.IntegerField(choices=NOTE_CHOICES)
    commentaire = models.TextField()
    date_publication = models.DateTimeField(default=timezone.now)
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plat = models.ForeignKey('Plat', on_delete=models.CASCADE, related_name='avis', null=True, blank=True)
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='avis', null=True, blank=True)

    def __str__(self):
        return f"Avis de {self.auteur}"
