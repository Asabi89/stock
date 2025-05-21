from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import json
from datetime import datetime, timedelta

from .models import (
    Category, Supplier, Product, Client as ClientModel,
    Purchase, PurchaseItem, Sale, SaleItem,
    Payment, StockMovement
)

class BaseTestCase(TestCase):
    """Classe de base pour les tests avec configuration commune"""
    
    def setUp(self):
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Créer un client HTTP
        self.client = Client()
        
        # Connecter l'utilisateur
        self.client.login(username='testuser', password='testpassword123')
        
        # Créer des données de base pour les tests
        self.category = Category.objects.create(
            name='Catégorie Test',
            description='Description de test'
        )
        
        self.supplier = Supplier.objects.create(
            name='Fournisseur Test',
            contact_person='Contact Test',
            phone='123456789',
            email='fournisseur@test.com',
            address='Adresse de test'
        )
        
        self.product = Product.objects.create(
            name='Produit Test',
            category=self.category,
            description='Description du produit test',
            purchase_price=Decimal('100.00'),
            selling_price=Decimal('150.00'),
            quantity=50,
            minimum_threshold=10,
            unit='pièce'
        )
        
        self.client_model = ClientModel.objects.create(
            name='Client Test',
            contact_person='Contact Client',
            phone='987654321',
            email='client@test.com',
            address='Adresse client test'
        )


class AuthenticationTests(TestCase):
    """Tests pour l'authentification"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')
    
    def test_login_page_loads(self):
        """Vérifier que la page de connexion se charge correctement"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/login.html')
    
    def test_login_success(self):
        """Vérifier qu'un utilisateur peut se connecter avec des identifiants valides"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        self.assertRedirects(response, self.dashboard_url)
        
    def test_login_failure(self):
        """Vérifier qu'un utilisateur ne peut pas se connecter avec des identifiants invalides"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Veuillez vérifier votre nom d'utilisateur et votre mot de passe")
    
    def test_dashboard_requires_login(self):
        """Vérifier que le tableau de bord nécessite une connexion"""
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.dashboard_url}')


class CategoryTests(BaseTestCase):
    """Tests pour la gestion des catégories"""
    
    def test_category_list(self):
        """Vérifier que la liste des catégories s'affiche correctement"""
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/category/list.html')
        self.assertContains(response, 'Catégorie Test')
    
    def test_category_create(self):
        """Vérifier qu'une catégorie peut être créée"""
        response = self.client.post(reverse('category_create'), {
            'name': 'Nouvelle Catégorie',
            'description': 'Description nouvelle catégorie'
        })
        self.assertRedirects(response, reverse('category_list'))
        self.assertTrue(Category.objects.filter(name='Nouvelle Catégorie').exists())
    
    def test_category_edit(self):
        """Vérifier qu'une catégorie peut être modifiée"""
        response = self.client.post(reverse('category_edit', args=[self.category.id]), {
            'name': 'Catégorie Modifiée',
            'description': 'Description modifiée'
        })
        self.assertRedirects(response, reverse('category_list'))
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Catégorie Modifiée')
    
    def test_category_delete(self):
        """Vérifier qu'une catégorie peut être supprimée"""
        response = self.client.post(reverse('category_delete', args=[self.category.id]))
        self.assertRedirects(response, reverse('category_list'))
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())


class ProductTests(BaseTestCase):
    """Tests pour la gestion des produits"""
    
    def test_product_list(self):
        """Vérifier que la liste des produits s'affiche correctement"""
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/product/list.html')
        self.assertContains(response, 'Produit Test')
    
    def test_product_create(self):
        """Vérifier qu'un produit peut être créé"""
        response = self.client.post(reverse('product_create'), {
            'name': 'Nouveau Produit',
            'category': self.category.id,
            'description': 'Description nouveau produit',
            'purchase_price': '200.00',
            'selling_price': '300.00',
            'quantity': 30,
            'minimum_threshold': 5,
            'unit': 'kg'
        })
        self.assertRedirects(response, reverse('product_list'))
        self.assertTrue(Product.objects.filter(name='Nouveau Produit').exists())
        
        # Vérifier qu'un mouvement de stock a été créé
        product = Product.objects.get(name='Nouveau Produit')
        self.assertTrue(StockMovement.objects.filter(
            product=product,
            movement_type='in',
            quantity=30,
            reference='Stock initial'
        ).exists())
    
    def test_product_edit(self):
        """Vérifier qu'un produit peut être modifié"""
        old_quantity = self.product.quantity
        new_quantity = old_quantity + 10
        
        response = self.client.post(reverse('product_edit', args=[self.product.id]), {
            'name': 'Produit Modifié',
            'category': self.category.id,
            'description': 'Description modifiée',
            'purchase_price': '120.00',
            'selling_price': '180.00',
            'quantity': new_quantity,
            'minimum_threshold': 15,
            'unit': 'pièce'
        })
        self.assertRedirects(response, reverse('product_list'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Produit Modifié')
        self.assertEqual(self.product.quantity, new_quantity)
        
        # Vérifier qu'un mouvement de stock a été créé pour l'ajustement
        self.assertTrue(StockMovement.objects.filter(
            product=self.product,
            movement_type='in',
            quantity=10,
            reference='Ajustement manuel'
        ).exists())
    
    def test_product_delete(self):
        """Vérifier qu'un produit peut être supprimé"""
        response = self.client.post(reverse('product_delete', args=[self.product.id]))
        self.assertRedirects(response, reverse('product_list'))
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())


class SupplierTests(BaseTestCase):
    """Tests pour la gestion des fournisseurs"""
    
    def test_supplier_list(self):
        """Vérifier que la liste des fournisseurs s'affiche correctement"""
        response = self.client.get(reverse('supplier_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/supplier/list.html')
        self.assertContains(response, 'Fournisseur Test')
    
    def test_supplier_create(self):
        """Vérifier qu'un fournisseur peut être créé"""
        response = self.client.post(reverse('supplier_create'), {
            'name': 'Nouveau Fournisseur',
            'contact_person': 'Nouveau Contact',
            'phone': '555666777',
            'email': 'nouveau@fournisseur.com',
            'address': 'Nouvelle adresse'
        })
        self.assertRedirects(response, reverse('supplier_list'))
        self.assertTrue(Supplier.objects.filter(name='Nouveau Fournisseur').exists())
    
    def test_supplier_edit(self):
        """Vérifier qu'un fournisseur peut être modifié"""
        response = self.client.post(reverse('supplier_edit', args=[self.supplier.id]), {
            'name': 'Fournisseur Modifié',
            'contact_person': 'Contact Modifié',
            'phone': '999888777',
            'email': 'modifie@fournisseur.com',
            'address': 'Adresse modifiée'
        })
        self.assertRedirects(response, reverse('supplier_list'))
        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.name, 'Fournisseur Modifié')
    
    def test_supplier_delete(self):
        """Vérifier qu'un fournisseur peut être supprimé"""
        response = self.client.post(reverse('supplier_delete', args=[self.supplier.id]))
        self.assertRedirects(response, reverse('supplier_list'))
        self.assertFalse(Supplier.objects.filter(id=self.supplier.id).exists())


class ClientTests(BaseTestCase):
    """Tests pour la gestion des clients"""
    
    def test_client_list(self):
        """Vérifier que la liste des clients s'affiche correctement"""
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/client/list.html')
        self.assertContains(response, 'Client Test')
    
    def test_client_create(self):
        """Vérifier qu'un client peut être créé"""
        response = self.client.post(reverse('client_create'), {
            'name': 'Nouveau Client',
            'contact_person': 'Nouveau Contact Client',
            'phone': '111222333',
            'email': 'nouveau@client.com',
            'address': 'Nouvelle adresse client'
        })
        self.assertRedirects(response, reverse('client_list'))
        self.assertTrue(ClientModel.objects.filter(name='Nouveau Client').exists())
    
    def test_client_edit(self):
        """Vérifier qu'un client peut être modifié"""
        response = self.client.post(reverse('client_edit', args=[self.client_model.id]), {
            'name': 'Client Modifié',
            'contact_person': 'Contact Client Modifié',
            'phone': '444555666',
            'email': 'modifie@client.com',
            'address': 'Adresse client modifiée'
        })
        self.assertRedirects(response, reverse('client_list'))
        self.client_model.refresh_from_db()
        self.assertEqual(self.client_model.name, 'Client Modifié')
    
    def test_client_delete(self):
        """Vérifier qu'un client peut être supprimé"""
        response = self.client.post(reverse('client_delete', args=[self.client_model.id]))
        self.assertRedirects(response, reverse('client_list'))
        self.assertFalse(ClientModel.objects.filter(id=self.client_model.id).exists())


class PurchaseTests(BaseTestCase):
    """Tests pour la gestion des achats"""
    
    def test_purchase_list(self):
        """Vérifier que la liste des achats s'affiche correctement"""
        # Créer un achat de test
        purchase = Purchase.objects.create(
            supplier=self.supplier,
            purchase_date=timezone.now(),
            total_amount=Decimal('500.00'),
            paid_amount=Decimal('300.00'),
            created_by=self.user
        )
        
        response = self.client.get(reverse('purchase_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/purchase/list.html')
        self.assertContains(response, self.supplier.name)
    
    def test_purchase_create(self):
        """Vérifier qu'un achat peut être créé"""
        initial_quantity = self.product.quantity
        
        # Données pour l'achat
        purchase_data = {
            'supplier': self.supplier.id,
            'purchase_date': timezone.now().strftime('%Y-%m-%d'),
            'items_data': json.dumps([{
                'product_id': self.product.id,
                'quantity': 10,
                'unit_price': 100.00
            }])
        }
        
        response = self.client.post(reverse('purchase_create'), purchase_data)
        self.assertRedirects(response, reverse('purchase_list'))
        
        # Vérifier que l'achat a été créé
        self.assertTrue(Purchase.objects.filter(supplier=self.supplier).exists())
        
        # Vérifier que le stock a été mis à jour
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity + 10)
        
        # Vérifier qu'un mouvement de stock a été créé
        purchase = Purchase.objects.filter(supplier=self.supplier).first()
        self.assertTrue(StockMovement.objects.filter(
                        product=self.product,
            movement_type='in',
            quantity=10,
            purchase=purchase
        ).exists())
    
    def test_purchase_detail(self):
        """Vérifier que les détails d'un achat s'affichent correctement"""
        # Créer un achat de test
        purchase = Purchase.objects.create(
            supplier=self.supplier,
            purchase_date=timezone.now(),
            total_amount=Decimal('500.00'),
            paid_amount=Decimal('300.00'),
            created_by=self.user
        )
        
        # Créer un élément d'achat
        purchase_item = PurchaseItem.objects.create(
            purchase=purchase,
            product=self.product,
            quantity=5,
            unit_price=Decimal('100.00')
        )
        
        response = self.client.get(reverse('purchase_detail', args=[purchase.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/purchase/detail.html')
        self.assertContains(response, self.product.name)
        self.assertContains(response, '500.00')


class SaleTests(BaseTestCase):
    """Tests pour la gestion des ventes"""
    
    def test_sale_list(self):
        """Vérifier que la liste des ventes s'affiche correctement"""
        # Créer une vente de test
        sale = Sale.objects.create(
            client=self.client_model,
            sale_date=timezone.now(),
            total_amount=Decimal('300.00'),
            paid_amount=Decimal('200.00'),
            created_by=self.user
        )
        
        response = self.client.get(reverse('sale_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/sale/list.html')
        self.assertContains(response, self.client_model.name)
    
    def test_sale_create(self):
        """Vérifier qu'une vente peut être créée"""
        initial_quantity = self.product.quantity
        
        # Données pour la vente
        sale_data = {
            'client': self.client_model.id,
            'sale_date': timezone.now().strftime('%Y-%m-%d'),
            'items_data': json.dumps([{
                'product_id': self.product.id,
                'quantity': 5,
                'unit_price': 150.00
            }])
        }
        
        response = self.client.post(reverse('sale_create'), sale_data)
        self.assertRedirects(response, reverse('sale_list'))
        
        # Vérifier que la vente a été créée
        self.assertTrue(Sale.objects.filter(client=self.client_model).exists())
        
        # Vérifier que le stock a été mis à jour
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity - 5)
        
        # Vérifier qu'un mouvement de stock a été créé
        sale = Sale.objects.filter(client=self.client_model).first()
        self.assertTrue(StockMovement.objects.filter(
            product=self.product,
            movement_type='out',
            quantity=5,
            sale=sale
        ).exists())
    
    def test_sale_insufficient_stock(self):
        """Vérifier qu'une vente ne peut pas être créée si le stock est insuffisant"""
        # Réduire le stock du produit
        self.product.quantity = 2
        self.product.save()
        
        # Données pour la vente avec une quantité supérieure au stock
        sale_data = {
            'client': self.client_model.id,
            'sale_date': timezone.now().strftime('%Y-%m-%d'),
            'items_data': json.dumps([{
                'product_id': self.product.id,
                'quantity': 10,  # Plus que le stock disponible
                'unit_price': 150.00
            }])
        }
        
        response = self.client.post(reverse('sale_create'), sale_data)
        self.assertRedirects(response, reverse('sale_create'))
        
        # Vérifier qu'aucune vente n'a été créée
        self.assertFalse(Sale.objects.filter(client=self.client_model).exists())
    
    def test_sale_detail(self):
        """Vérifier que les détails d'une vente s'affichent correctement"""
        # Créer une vente de test
        sale = Sale.objects.create(
            client=self.client_model,
            sale_date=timezone.now(),
            total_amount=Decimal('300.00'),
            paid_amount=Decimal('200.00'),
            created_by=self.user
        )
        
        # Créer un élément de vente
        sale_item = SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=2,
            unit_price=Decimal('150.00')
        )
        
        response = self.client.get(reverse('sale_detail', args=[sale.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/sale/detail.html')
        self.assertContains(response, self.product.name)
        self.assertContains(response, '300.00')
    
    def test_generate_invoice_pdf(self):
        """Vérifier que la génération de facture PDF fonctionne"""
        # Créer une vente de test
        sale = Sale.objects.create(
            client=self.client_model,
            sale_date=timezone.now(),
            total_amount=Decimal('300.00'),
            paid_amount=Decimal('200.00'),
            created_by=self.user
        )
        
        # Créer un élément de vente
        sale_item = SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=2,
            unit_price=Decimal('150.00')
        )
        
        response = self.client.get(reverse('generate_invoice_pdf', args=[sale.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename="facture_'))


class PaymentTests(BaseTestCase):
    """Tests pour la gestion des paiements"""
    
    def setUp(self):
        super().setUp()
        
        # Créer un achat de test
        self.purchase = Purchase.objects.create(
            supplier=self.supplier,
            purchase_date=timezone.now(),
            total_amount=Decimal('500.00'),
            paid_amount=Decimal('0.00'),
            created_by=self.user
        )
        
        # Créer une vente de test
        self.sale = Sale.objects.create(
            client=self.client_model,
            sale_date=timezone.now(),
            total_amount=Decimal('300.00'),
            paid_amount=Decimal('0.00'),
            created_by=self.user
        )
    
    def test_payment_list(self):
        """Vérifier que la liste des paiements s'affiche correctement"""
        # Créer un paiement client
        client_payment = Payment.objects.create(
            payment_type='client',
            payment_method='cash',
            amount=Decimal('100.00'),
            payment_date=timezone.now(),
            sale=self.sale,
            created_by=self.user
        )
        
        # Créer un paiement fournisseur
        supplier_payment = Payment.objects.create(
            payment_type='supplier',
            payment_method='bank_transfer',
            amount=Decimal('200.00'),
            payment_date=timezone.now(),
            purchase=self.purchase,
            created_by=self.user
        )
        
        response = self.client.get(reverse('payment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/payment/list.html')
        self.assertContains(response, '100.00')
        self.assertContains(response, '200.00')
    
    def test_client_payment_create(self):
        """Vérifier qu'un paiement client peut être créé"""
        payment_data = {
            'sale': self.sale.id,
            'payment_method': 'cash',
            'amount': '150.00',
            'payment_date': timezone.now().strftime('%Y-%m-%d'),
            'notes': 'Paiement test client'
        }
        
        response = self.client.post(reverse('client_payment_create'), payment_data)
        self.assertRedirects(response, reverse('payment_list'))
        
        # Vérifier que le paiement a été créé
        self.assertTrue(Payment.objects.filter(
            payment_type='client',
            sale=self.sale,
            amount=Decimal('150.00')
        ).exists())
        
        # Vérifier que le montant payé de la vente a été mis à jour
        self.sale.refresh_from_db()
        self.assertEqual(self.sale.paid_amount, Decimal('150.00'))
    
    def test_supplier_payment_create(self):
        """Vérifier qu'un paiement fournisseur peut être créé"""
        payment_data = {
            'purchase': self.purchase.id,
            'payment_method': 'bank_transfer',
            'amount': '250.00',
            'payment_date': timezone.now().strftime('%Y-%m-%d'),
            'notes': 'Paiement test fournisseur'
        }
        
        response = self.client.post(reverse('supplier_payment_create'), payment_data)
        self.assertRedirects(response, reverse('payment_list'))
        
        # Vérifier que le paiement a été créé
        self.assertTrue(Payment.objects.filter(
            payment_type='supplier',
            purchase=self.purchase,
            amount=Decimal('250.00')
        ).exists())
        
        # Vérifier que le montant payé de l'achat a été mis à jour
        self.purchase.refresh_from_db()
        self.assertEqual(self.purchase.paid_amount, Decimal('250.00'))


class ReportTests(BaseTestCase):
    """Tests pour les rapports et statistiques"""
    
    def setUp(self):
        super().setUp()
        
        # Créer des achats
        self.purchase1 = Purchase.objects.create(
            supplier=self.supplier,
            purchase_date=timezone.now() - timedelta(days=5),
            total_amount=Decimal('500.00'),
            paid_amount=Decimal('500.00'),
            created_by=self.user
        )
        
        self.purchase2 = Purchase.objects.create(
            supplier=self.supplier,
            purchase_date=timezone.now() - timedelta(days=2),
            total_amount=Decimal('300.00'),
            paid_amount=Decimal('150.00'),
            created_by=self.user
        )
        
        # Créer des ventes
        self.sale1 = Sale.objects.create(
            client=self.client_model,
            sale_date=timezone.now() - timedelta(days=4),
            total_amount=Decimal('200.00'),
            paid_amount=Decimal('200.00'),
            created_by=self.user
        )
        
        self.sale2 = Sale.objects.create(
            client=self.client_model,
            sale_date=timezone.now() - timedelta(days=1),
            total_amount=Decimal('350.00'),
            paid_amount=Decimal('200.00'),
            created_by=self.user
        )
        
        # Créer des éléments d'achat et de vente
        PurchaseItem.objects.create(
            purchase=self.purchase1,
            product=self.product,
            quantity=5,
            unit_price=Decimal('100.00')
        )
        
        PurchaseItem.objects.create(
            purchase=self.purchase2,
            product=self.product,
            quantity=3,
            unit_price=Decimal('100.00')
        )
        
        SaleItem.objects.create(
            sale=self.sale1,
            product=self.product,
            quantity=2,
            unit_price=Decimal('100.00')
        )
        
        SaleItem.objects.create(
            sale=self.sale2,
            product=self.product,
            quantity=3,
            unit_price=Decimal('116.67')
        )
    
    def test_stock_report(self):
        """Vérifier que le rapport de stock s'affiche correctement"""
        response = self.client.get(reverse('stock_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/reports/stock_report.html')
        self.assertContains(response, self.product.name)
    
    def test_sales_report(self):
        """Vérifier que le rapport des ventes s'affiche correctement"""
        response = self.client.get(reverse('sales_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/reports/sales_report.html')
        self.assertContains(response, '550.00')  # Total des ventes
        self.assertContains(response, '400.00')  # Total payé
    
    def test_sales_report_with_date_filter(self):
        """Vérifier que le filtre de date fonctionne pour le rapport des ventes"""
        # Filtrer sur les 3 derniers jours
        today = timezone.now().date()
        start_date = (today - timedelta(days=3)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = self.client.get(reverse('sales_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/reports/sales_report.html')
        self.assertContains(response, '350.00')  # Total de la vente2 uniquement
        self.assertContains(response, '200.00')  # Montant payé de la vente2
    
    def test_purchases_report(self):
        """Vérifier que le rapport des achats s'affiche correctement"""
        response = self.client.get(reverse('purchases_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/reports/purchases_report.html')
        self.assertContains(response, '800.00')  # Total des achats
        self.assertContains(response, '650.00')  # Total payé
    
    def test_purchases_report_with_date_filter(self):
        """Vérifier que le filtre de date fonctionne pour le rapport des achats"""
        # Filtrer sur les 3 derniers jours
        today = timezone.now().date()
        start_date = (today - timedelta(days=3)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = self.client.get(reverse('purchases_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/reports/purchases_report.html')
        self.assertContains(response, '300.00')  # Total de l'achat2 uniquement
        self.assertContains(response, '150.00')  # Montant payé de l'achat2
    
    def test_export_stock_csv(self):
        """Vérifier que l'exportation du stock en CSV fonctionne"""
        response = self.client.get(reverse('export_stock_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename="stock_report.csv"'))
        
        # Vérifier le contenu du CSV
        content = response.content.decode('utf-8')
        self.assertIn(self.product.name, content)
        self.assertIn(str(self.product.quantity), content)
    
    def test_export_purchases_report(self):
        """Vérifier que l'exportation du rapport des achats fonctionne"""
        response = self.client.get(reverse('export_purchases_report'), {
            'format': 'pdf',
            'include_charts': '1',
            'include_details': '1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename="purchases_report.pdf"'))
    
    def test_export_payments(self):
        """Vérifier que l'exportation des paiements fonctionne"""
        # Créer des paiements pour le test
        Payment.objects.create(
            payment_type='client',
            payment_method='cash',
            amount=Decimal('100.00'),
            payment_date=timezone.now(),
            sale=self.sale1,
            created_by=self.user
        )
        
        Payment.objects.create(
            payment_type='supplier',
            payment_method='bank_transfer',
            amount=Decimal('200.00'),
            payment_date=timezone.now(),
            purchase=self.purchase1,
            created_by=self.user
        )
        
        response = self.client.get(reverse('export_payments'), {
            'format': 'csv',
            'include_client': '1',
            'include_supplier': '1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename="payments_report.csv"'))
        
        # Vérifier le contenu du CSV
        content = response.content.decode('utf-8')
        self.assertIn('100.00', content)
        self.assertIn('200.00', content)


class APITests(BaseTestCase):
    """Tests pour les API"""
    
    def test_get_product_info(self):
        """Vérifier que l'API pour obtenir les informations d'un produit fonctionne"""
        response = self.client.get(reverse('get_product_info', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['id'], self.product.id)
        self.assertEqual(data['name'], self.product.name)
        self.assertEqual(data['purchase_price'], float(self.product.purchase_price))
        self.assertEqual(data['selling_price'], float(self.product.selling_price))
        self.assertEqual(data['quantity'], self.product.quantity)
        self.assertEqual(data['unit'], self.product.unit)
    
    def test_get_product_info_not_found(self):
        """Vérifier que l'API renvoie une erreur 404 pour un produit inexistant"""
        response = self.client.get(reverse('get_product_info', args=[9999]))  # ID inexistant
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Produit non trouvé')


class StockMovementTests(BaseTestCase):
    """Tests pour les mouvements de stock"""
    
    def test_stock_movement_creation_with_purchase(self):
        """Vérifier que les mouvements de stock sont créés lors d'un achat"""
        initial_quantity = self.product.quantity
        
        # Créer un achat
        purchase = Purchase.objects.create(
            supplier=self.supplier,
            purchase_date=timezone.now(),
            total_amount=Decimal('500.00'),
            paid_amount=Decimal('300.00'),
            created_by=self.user
        )
        
        # Créer un élément d'achat
        purchase_item = PurchaseItem.objects.create(
            purchase=purchase,
            product=self.product,
            quantity=10,
            unit_price=Decimal('50.00')
        )
        
        # Mettre à jour le stock du produit (comme dans la vue)
        self.product.quantity += 10
        self.product.save()
        
        # Créer un mouvement de stock
        stock_movement = StockMovement.objects.create(
            product=self.product,
            movement_type='in',
            quantity=10,
            reference=f'Achat #{purchase.id}',
            purchase=purchase,
            created_by=self.user
        )
        
        # Vérifier que le mouvement de stock a été créé correctement
        self.assertEqual(stock_movement.movement_type, 'in')
        self.assertEqual(stock_movement.quantity, 10)
        self.assertEqual(stock_movement.purchase, purchase)
        
        # Vérifier que le stock du produit a été mis à jour
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity + 10)
    
    def test_stock_movement_creation_with_sale(self):
        """Vérifier que les mouvements de stock sont créés lors d'une vente"""
        initial_quantity = self.product.quantity
        
        # Créer une vente
        sale = Sale.objects.create(
            client=self.client_model,
            sale_date=timezone.now(),
            total_amount=Decimal('300.00'),
            paid_amount=Decimal('200.00'),
            created_by=self.user
        )
        
        # Créer un élément de vente
        sale_item = SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=5,
            unit_price=Decimal('60.00')
        )
        
        # Mettre à jour le stock du produit (comme dans la vue)
        self.product.quantity -= 5
        self.product.save()
        
        # Créer un mouvement de stock
        stock_movement = StockMovement.objects.create(
            product=self.product,
            movement_type='out',
            quantity=5,
            reference=f'Vente #{sale.id}',
            sale=sale,
            created_by=self.user
        )
        
        # Vérifier que le mouvement de stock a été créé correctement
        self.assertEqual(stock_movement.movement_type, 'out')
        self.assertEqual(stock_movement.quantity, 5)
        self.assertEqual(stock_movement.sale, sale)
        
        # Vérifier que le stock du produit a été mis à jour
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity - 5)


class DashboardTests(BaseTestCase):
    """Tests pour le tableau de bord"""
    
    def setUp(self):
        super().setUp()
        
        # Créer des ventes récentes
        for i in range(3):
            sale = Sale.objects.create(
                client=self.client_model,
                sale_date=timezone.now() - timedelta(days=i),
                total_amount=Decimal(f'{(i+1)*100}.00'),
                paid_amount=Decimal(f'{(i+1)*50}.00'),
                created_by=self.user
            )
            
            # Créer un élément de vente
            SaleItem.objects.create(
                sale=sale,
                product=self.product,
                quantity=i+1,
                unit_price=Decimal('100.00')
            )
        
        # Créer des achats récents
        for i in range(2):
            purchase = Purchase.objects.create(
                supplier=self.supplier,
                purchase_date=timezone.now() - timedelta(days=i),
                total_amount=Decimal(f'{(i+1)*200}.00'),
                paid_amount=Decimal(f'{(i+1)*100}.00'),
                created_by=self.user
            )
            
            # Créer un élément d'achat
            PurchaseItem.objects.create(
                purchase=purchase,
                product=self.product,
                quantity=i+2,
                unit_price=Decimal('100.00')
            )
    
    def test_dashboard_loads(self):
        """Vérifier que le tableau de bord se charge correctement"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/dashboard.html')
        
        # Vérifier que les statistiques sont présentes
        self.assertContains(response, 'Produits en stock')
        self.assertContains(response, 'Produits en rupture')
        self.assertContains(response, 'Fournisseurs')
        self.assertContains(response, 'Clients')
        
        # Vérifier que les ventes récentes sont affichées
        self.assertContains(response, 'Ventes récentes')
        
        # Vérifier que les produits les plus vendus sont affichés
        self.assertContains(response, 'Produits les plus vendus')
        
        # Vérifier que les achats récents sont affichés
        self.assertContains(response, 'Achats récents')
        
        # Vérifier que les données pour le graphique sont présentes
        self.assertIn('sales_by_day', response.context)
        sales_by_day = json.loads(response.context['sales_by_day'])
        self.assertTrue(isinstance(sales_by_day, list))


class PrintTests(BaseTestCase):
    """Tests pour les fonctionnalités d'impression"""
    
    def test_print_purchase(self):
        """Vérifier que l'impression d'un bon d'achat fonctionne"""
        # Créer un achat de test
        purchase = Purchase.objects.create(
            supplier=self.supplier,
            purchase_date=timezone.now(),
            total_amount=Decimal('500.00'),
            paid_amount=Decimal('300.00'),
            created_by=self.user
        )
        
        # Créer un élément d'achat
        purchase_item = PurchaseItem.objects.create(
            purchase=purchase,
            product=self.product,
            quantity=5,
            unit_price=Decimal('100.00')
        )
        
        response = self.client.get(reverse('print_purchase', args=[purchase.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith(f'attachment; filename="bon_achat_{purchase.id}.pdf"'))
