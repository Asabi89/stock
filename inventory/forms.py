from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import (
    Category, Supplier, Product, Client,
    Purchase, PurchaseItem, Sale, SaleItem, Payment
)

# Enhanced form field classes with better visibility
FORM_FIELD_CLASS = (
    'w-full px-4 py-3 border-2 rounded-lg transition-all duration-200 '
    'bg-white shadow-sm hover:shadow focus:shadow-md '
    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 '
    'border-secondary-300 border-l-4 border-l-primary-500'
)

SELECT_FIELD_CLASS = (
    'w-full px-4 py-3 border-2 rounded-lg transition-all duration-200 '
    'bg-white shadow-sm hover:shadow focus:shadow-md '
    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 '
    'border-secondary-300 border-l-4 border-l-primary-500 '
    'appearance-none bg-no-repeat bg-right'
)

TEXTAREA_FIELD_CLASS = (
    'w-full px-4 py-3 border-2 rounded-lg transition-all duration-200 '
    'bg-white shadow-sm hover:shadow focus:shadow-md '
    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 '
    'border-secondary-300 border-l-4 border-l-primary-500 resize-none'
)

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': FORM_FIELD_CLASS,
            'placeholder': 'Nom d\'utilisateur',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': FORM_FIELD_CLASS,
            'placeholder': 'Mot de passe',
            'autocomplete': 'current-password',
        })
    )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Nom de la catégorie',
                'maxlength': '50',
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_FIELD_CLASS,
                'rows': 3,
                'placeholder': 'Description détaillée de la catégorie',
                'maxlength': '255',
            }),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Nom du fournisseur',
            }),
            'contact_person': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Personne à contacter',
            }),
            'phone': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Numéro de téléphone',
                'type': 'tel',
            }),
            'email': forms.EmailInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Adresse email',
            }),
            'address': forms.Textarea(attrs={
                'class': TEXTAREA_FIELD_CLASS,
                'rows': 3,
                'placeholder': 'Adresse complète',
            }),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'purchase_price',
                 'selling_price', 'quantity', 'minimum_threshold', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Nom du produit',
            }),
            'category': forms.Select(attrs={
                'class': SELECT_FIELD_CLASS,
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_FIELD_CLASS,
                'rows': 3,
                'placeholder': 'Description du produit',
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'step': '0.01',
                'min': '0',
                'placeholder': 'Prix d\'achat',
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'step': '0.01',
                'min': '0',
                'placeholder': 'Prix de vente',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'min': '0',
                'placeholder': 'Quantité en stock',
            }),
            'minimum_threshold': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'min': '0',
                'placeholder': 'Seuil d\'alerte',
            }),
            'unit': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Unité (ex: kg, pièce, litre)',
            }),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Nom du client',
            }),
            'phone': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Numéro de téléphone',
                'type': 'tel',
            }),
            'email': forms.EmailInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Adresse email',
            }),
            'address': forms.Textarea(attrs={
                'class': TEXTAREA_FIELD_CLASS,
                'rows': 3,
                'placeholder': 'Adresse complète',
            }),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'purchase_date', 'total_amount', 'paid_amount']
        widgets = {
            'supplier': forms.Select(attrs={
                'class': SELECT_FIELD_CLASS,
            }),
            'purchase_date': forms.DateTimeInput(attrs={
                'class': FORM_FIELD_CLASS,
                'type': 'datetime-local',
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS + ' bg-secondary-50',
                'step': '0.01',
                'readonly': 'readonly',
                'placeholder': 'Calculé automatiquement',
            }),
            'paid_amount': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'step': '0.01',
                'min': '0',
                'placeholder': 'Montant payé',
            }),
        }

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': SELECT_FIELD_CLASS,
            }),
            'quantity': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'min': '1',
                'placeholder': 'Quantité',
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'step': '0.01',
                'min': '0',
                'placeholder': 'Prix unitaire',
            }),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['client', 'sale_date', 'total_amount', 'paid_amount']
        widgets = {
            'client': forms.Select(attrs={
                'class': SELECT_FIELD_CLASS,
            }),
            'sale_date': forms.DateTimeInput(attrs={
                'class': FORM_FIELD_CLASS,
                'type': 'datetime-local',
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS + ' bg-secondary-50',
                'step': '0.01',
                'readonly': 'readonly',
                'placeholder': 'Calculé automatiquement',
            }),
            'paid_amount': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'step': '0.01',
                'min': '0',
                'placeholder': 'Montant payé',
            }),
        }

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': SELECT_FIELD_CLASS,
            }),
            'quantity': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'min': '1',
                'placeholder': 'Quantité',
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'step': '0.01',
                'min': '0',
                'placeholder': 'Prix unitaire',
            }),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_type', 'payment_method', 'amount', 'payment_date', 'notes']
        widgets = {
            'payment_type': forms.Select(attrs={
                'class': SELECT_FIELD_CLASS,
            }),
            'payment_method': forms.Select(attrs={
                'class': SELECT_FIELD_CLASS,
            }),
            'amount': forms.NumberInput(attrs={
                'class': FORM_FIELD_CLASS,
                'step': '0.01',
                'min': '0',
                'placeholder': 'Montant',
            }),
            'payment_date': forms.DateTimeInput(attrs={
                'class': FORM_FIELD_CLASS,
                'type': 'datetime-local',
            }),
            'notes': forms.Textarea(attrs={
                'class': TEXTAREA_FIELD_CLASS,
                'rows': 3,
                'placeholder': 'Notes ou commentaires',
            }),
        }

class ClientPaymentForm(PaymentForm):
    sale = forms.ModelChoiceField(
        queryset=Sale.objects.filter(payment_status__in=['unpaid', 'partial']),
        widget=forms.Select(attrs={
            'class': SELECT_FIELD_CLASS,
        })
    )
    
    class Meta(PaymentForm.Meta):
        fields = ['sale', 'payment_method', 'amount', 'payment_date', 'notes']

class SupplierPaymentForm(PaymentForm):
    purchase = forms.ModelChoiceField(
        queryset=Purchase.objects.all(),
        widget=forms.Select(attrs={
            'class': SELECT_FIELD_CLASS,
        })
    )
    
    class Meta(PaymentForm.Meta):
        fields = ['purchase', 'payment_method', 'amount', 'payment_date', 'notes']
