from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du fournisseur")
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="Personne de contact")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(blank=True, null=True, verbose_name="Adresse")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du produit")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix d'achat")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de vente")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantité en stock")
    minimum_threshold = models.PositiveIntegerField(default=5, verbose_name="Seuil minimum")
    unit = models.CharField(max_length=20, default="pièce", verbose_name="Unité")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_threshold

class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du client")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(blank=True, null=True, verbose_name="Adresse")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Fournisseur")
    purchase_date = models.DateTimeField(default=timezone.now, verbose_name="Date d'achat")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant payé")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Achat"
        verbose_name_plural = "Achats"
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"Achat #{self.id} - {self.supplier.name}"
    
    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount
    
    @property
    def is_fully_paid(self):
        return self.paid_amount >= self.total_amount

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE, verbose_name="Achat")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    quantity = models.PositiveIntegerField(verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")
    
    class Meta:
        verbose_name = "Élément d'achat"
        verbose_name_plural = "Éléments d'achat"
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price

class Sale(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Payé'),
        ('partial', 'Partiellement payé'),
        ('unpaid', 'Non payé'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Client")
    sale_date = models.DateTimeField(default=timezone.now, verbose_name="Date de vente")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant payé")
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid', verbose_name="Statut de paiement")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-sale_date']
    
    def __str__(self):
        client_name = self.client.name if self.client else "Client anonyme"
        return f"Vente #{self.id} - {client_name}"
    
    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount
    
    def save(self, *args, **kwargs):
        if self.paid_amount >= self.total_amount:
            self.payment_status = 'paid'
        elif self.paid_amount > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'unpaid'
        super().save(*args, **kwargs)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE, verbose_name="Vente")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    quantity = models.PositiveIntegerField(verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")
    
    class Meta:
        verbose_name = "Élément de vente"
        verbose_name_plural = "Éléments de vente"
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('client', 'Paiement client'),
        ('supplier', 'Paiement fournisseur'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Espèces'),
        ('mobile_money', 'Mobile Money'),
        ('check', 'Chèque'),
        ('bank_transfer', 'Virement bancaire'),
        ('other', 'Autre'),
    ]
    
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, verbose_name="Type de paiement")
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES, default='cash', verbose_name="Méthode de paiement")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    payment_date = models.DateTimeField(default=timezone.now, verbose_name="Date de paiement")
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vente associée")
    purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Achat associé")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Paiement #{self.id} - {self.get_payment_type_display()}"


class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'Entrée'),
        ('out', 'Sortie'),
        ('adjustment', 'Ajustement'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPE_CHOICES, verbose_name="Type de mouvement")
    quantity = models.PositiveIntegerField(verbose_name="Quantité")
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="Référence")
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vente associée")
    purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Achat associé")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"
