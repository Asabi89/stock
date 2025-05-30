# Generated by Django 5.2.1 on 2025-05-08 10:21

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom de la catégorie')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
            ],
            options={
                'verbose_name': 'Catégorie',
                'verbose_name_plural': 'Catégories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom du client')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Téléphone')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('address', models.TextField(blank=True, null=True, verbose_name='Adresse')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom du fournisseur')),
                ('contact_person', models.CharField(blank=True, max_length=100, null=True, verbose_name='Personne de contact')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Téléphone')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('address', models.TextField(blank=True, null=True, verbose_name='Adresse')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
            ],
            options={
                'verbose_name': 'Fournisseur',
                'verbose_name_plural': 'Fournisseurs',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom du produit')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Prix d'achat")),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Prix de vente')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='Quantité en stock')),
                ('minimum_threshold', models.PositiveIntegerField(default=5, verbose_name='Seuil minimum')),
                ('unit', models.CharField(default='pièce', max_length=20, verbose_name='Unité')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.category', verbose_name='Catégorie')),
            ],
            options={
                'verbose_name': 'Produit',
                'verbose_name_plural': 'Produits',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date d'achat")),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Montant total')),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Montant payé')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Créé par')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.supplier', verbose_name='Fournisseur')),
            ],
            options={
                'verbose_name': 'Achat',
                'verbose_name_plural': 'Achats',
                'ordering': ['-purchase_date'],
            },
        ),
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantité')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Prix unitaire')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product', verbose_name='Produit')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.purchase', verbose_name='Achat')),
            ],
            options={
                'verbose_name': "Élément d'achat",
                'verbose_name_plural': "Éléments d'achat",
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de vente')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Montant total')),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Montant payé')),
                ('payment_status', models.CharField(choices=[('paid', 'Payé'), ('partial', 'Partiellement payé'), ('unpaid', 'Non payé')], default='unpaid', max_length=10, verbose_name='Statut de paiement')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.client', verbose_name='Client')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Créé par')),
            ],
            options={
                'verbose_name': 'Vente',
                'verbose_name_plural': 'Ventes',
                'ordering': ['-sale_date'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(choices=[('client', 'Paiement client'), ('supplier', 'Paiement fournisseur')], max_length=10, verbose_name='Type de paiement')),
                ('payment_method', models.CharField(choices=[('cash', 'Espèces'), ('mobile_money', 'Mobile Money'), ('check', 'Chèque'), ('bank_transfer', 'Virement bancaire'), ('other', 'Autre')], default='cash', max_length=15, verbose_name='Méthode de paiement')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Montant')),
                ('payment_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de paiement')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Créé par')),
                ('purchase', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.purchase', verbose_name='Achat associé')),
                ('sale', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.sale', verbose_name='Vente associée')),
            ],
            options={
                'verbose_name': 'Paiement',
                'verbose_name_plural': 'Paiements',
                'ordering': ['-payment_date'],
            },
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantité')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Prix unitaire')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product', verbose_name='Produit')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.sale', verbose_name='Vente')),
            ],
            options={
                'verbose_name': 'Élément de vente',
                'verbose_name_plural': 'Éléments de vente',
            },
        ),
        migrations.CreateModel(
            name='StockMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movement_type', models.CharField(choices=[('in', 'Entrée'), ('out', 'Sortie'), ('adjustment', 'Ajustement')], max_length=10, verbose_name='Type de mouvement')),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantité')),
                ('reference', models.CharField(blank=True, max_length=100, null=True, verbose_name='Référence')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Créé par')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product', verbose_name='Produit')),
                ('purchase', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.purchase', verbose_name='Achat associé')),
                ('sale', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.sale', verbose_name='Vente associée')),
            ],
            options={
                'verbose_name': 'Mouvement de stock',
                'verbose_name_plural': 'Mouvements de stock',
                'ordering': ['-created_at'],
            },
        ),
    ]
