from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from import_export.admin import ImportExportModelAdmin
from .models import (
    Category, Supplier, Product, Client, 
    Purchase, PurchaseItem, Sale, SaleItem, 
    Payment, StockMovement
)

# Custom filter for is_low_stock property
class LowStockFilter(SimpleListFilter):
    title = 'stock status'
    parameter_name = 'is_low_stock'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Low Stock'),
            ('no', 'Sufficient Stock'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(quantity__lte=models.F('minimum_threshold'))
        if self.value() == 'no':
            return queryset.filter(quantity__gt=models.F('minimum_threshold'))

# Custom filter for is_fully_paid property
class FullyPaidFilter(SimpleListFilter):
    title = 'payment status'
    parameter_name = 'is_fully_paid'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Fully Paid'),
            ('no', 'Not Fully Paid'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(paid_amount__gte=models.F('total_amount'))
        if self.value() == 'no':
            return queryset.filter(paid_amount__lt=models.F('total_amount'))

class CategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)

class SupplierAdmin(ImportExportModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'created_at')
    search_fields = ('name', 'contact_person', 'phone', 'email')

class ProductAdmin(ImportExportModelAdmin):
    list_display = ('name', 'category', 'purchase_price', 'selling_price', 'quantity', 'minimum_threshold', 'is_low_stock', 'updated_at')
    list_filter = ('category', LowStockFilter)  # Use custom filter instead of property
    search_fields = ('name', 'description')

class ClientAdmin(ImportExportModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

class PurchaseAdmin(ImportExportModelAdmin):
    list_display = ('id', 'supplier', 'purchase_date', 'total_amount', 'paid_amount', 'balance_due', 'is_fully_paid', 'created_by')
    list_filter = ('supplier', 'purchase_date', FullyPaidFilter)  # Use custom filter instead of property
    search_fields = ('supplier__name',)
    inlines = [PurchaseItemInline]

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

class SaleAdmin(ImportExportModelAdmin):
    list_display = ('id', 'client', 'sale_date', 'total_amount', 'paid_amount', 'balance_due', 'payment_status', 'created_by')
    list_filter = ('client', 'sale_date', 'payment_status')
    search_fields = ('client__name',)
    inlines = [SaleItemInline]

class PaymentAdmin(ImportExportModelAdmin):
    list_display = ('id', 'payment_type', 'payment_method', 'amount', 'payment_date', 'created_by')
    list_filter = ('payment_type', 'payment_method', 'payment_date')
    search_fields = ('notes',)

class StockMovementAdmin(ImportExportModelAdmin):
    list_display = ('id', 'product', 'movement_type', 'quantity', 'reference', 'created_at', 'created_by')
    list_filter = ('movement_type', 'product', 'created_at')
    search_fields = ('product__name', 'reference', 'notes')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(StockMovement, StockMovementAdmin)
