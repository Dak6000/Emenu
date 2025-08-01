from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Plat, Menu, Avis

User = get_user_model()


class PlatForm(forms.ModelForm):
    nom = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom du plat'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Description détaillée du plat'
        })
    )
    prix = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prix (en Fcfa)',
            'step': '0.01'
        })
    )
    categorie = forms.ChoiceField(
        choices=Plat.CATEGORIES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    disponibilite = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        initial=True
    )
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = Plat
        fields = ['nom', 'description', 'prix', 'categorie', 'disponibilite', 'photo']

    def clean_prix(self):
        prix = self.cleaned_data.get('prix')
        if prix <= 0:
            raise ValidationError("Le prix doit être supérieur à zéro.")
        return prix


class MenuForm(forms.ModelForm):
    nom = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom du menu'
        })
    )
    status = forms.ChoiceField(
        choices=Menu.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    plats = forms.ModelMultipleChoiceField(
        queryset=Plat.objects.none(),  # Sera surchargé dans __init__
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=True
    )

    class Meta:
        model = Menu
        fields = ['nom', 'status', 'plats']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['plats'].queryset = Plat.objects.filter(createur=user)

    def clean_plats(self):
        plats = self.cleaned_data.get('plats')
        if not plats:
            raise ValidationError("Vous devez sélectionner au moins un plat.")
        return plats


class AvisForm(forms.ModelForm):
    note = forms.ChoiceField(
        choices=Avis.NOTE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    commentaire = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Votre commentaire...'
        })
    )

    class Meta:
        model = Avis
        fields = ['note', 'commentaire']

    def clean_commentaire(self):
        commentaire = self.cleaned_data.get('commentaire')
        if len(commentaire) < 10:
            raise ValidationError("Le commentaire doit contenir au moins 10 caractères.")
        return commentaire