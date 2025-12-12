from django.contrib import admin
from .models import PaymentMethod, Payment


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'type', 'is_active', 'ordering']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'code', 'description']
    list_editable = ['ordering', 'is_active']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'payment_method', 'amount', 'currency', 
                    'status', 'created_at']
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = ['uuid', 'created_at', 'updated_at', 'authorized_at', 
                       'captured_at']
    date_hierarchy = 'created_at'
