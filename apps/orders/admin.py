from django.contrib import admin
from .models import Order, OrderItem, QuickOrder


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'variant', 'product_name', 'price', 'quantity', 
                       'tax_rate', 'total_price']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'customer_phone', 'total', 
                    'payment_status', 'status', 'created_at']
    list_filter = ['status', 'payment_status', 'order_type', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email', 
                    'customer_phone']
    readonly_fields = ['uuid', 'order_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('uuid', 'order_number', 'order_type', 'status')
        }),
        ('معلومات العميل', {
            'fields': ('customer', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('معلومات الشحن', {
            'fields': ('shipping_country', 'shipping_city', 'shipping_district',
                      'shipping_address', 'shipping_building_number', 
                      'shipping_postal_code')
        }),
        ('المبالغ المالية', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 
                      'discount_amount', 'total')
        }),
        ('الدفع', {
            'fields': ('payment_method', 'payment_status')
        }),
        ('ملاحظات', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 
                      'shipped_at', 'delivered_at')
        }),
    )
    
    inlines = [OrderItemInline]
    
    actions = ['mark_as_confirmed', 'mark_as_processing', 'mark_as_shipped']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status=Order.Status.CONFIRMED)
    mark_as_confirmed.short_description = 'تأكيد الطلبات المختارة'
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status=Order.Status.PROCESSING)
    mark_as_processing.short_description = 'تحديد كـ قيد المعالجة'
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)
    mark_as_shipped.short_description = 'تحديد كـ تم الشحن'


@admin.register(QuickOrder)
class QuickOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'product', 'quantity', 
                    'city', 'status', 'created_at']
    list_filter = ['status', 'city', 'created_at']
    search_fields = ['name', 'phone_number', 'email', 'product__name']
    readonly_fields = ['ip_address', 'user_agent', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_confirmed', 'mark_as_processing']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status=QuickOrder.OrderStatus.CONFIRMED)
    mark_as_confirmed.short_description = 'تأكيد الطلبات المختارة'
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status=QuickOrder.OrderStatus.PROCESSING)
    mark_as_processing.short_description = 'تحديد كـ قيد المعالجة'
