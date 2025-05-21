from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Authentification
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Tableau de bord
    path('', views.dashboard, name='dashboard'),
    
    # Catégories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Fournisseurs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # Produits
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:product_id>/info/', views.get_product_info, name='get_product_info'),
    
    # Clients
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:pk>/edit/', views.client_edit, name='client_edit'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
    
    # Achats
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/create/', views.purchase_create, name='purchase_create'),
    path('purchases/<int:pk>/', views.purchase_detail, name='purchase_detail'),
    
    # Ventes
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/invoice/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    
    # Paiements
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/client/create/', views.client_payment_create, name='client_payment_create'),
    path('payments/supplier/create/', views.supplier_payment_create, name='supplier_payment_create'),
    
    # Rapports
    path('reports/stock/', views.stock_report, name='stock_report'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/purchases/', views.purchases_report, name='purchases_report'),
    path('reports/stock/export/csv/', views.export_stock_csv, name='export_stock_csv'),
    path('payments/export/', views.export_payments, name='export_payments'),
    path('purchases/<int:pk>/print/', views.print_purchase, name='print_purchase'),
    path('reports/purchases/export/', views.export_purchases_report, name='export_purchases_report'),


]
