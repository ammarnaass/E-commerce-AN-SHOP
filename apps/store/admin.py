from django.contrib import admin
from django.utils.html import format_html
from .models import (Category, Brand, Product, ProductImage, 
                     Attribute, AttributeValue, ProductVariant)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'ordering', 'products_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['ordering', 'is_active']
    
    def products_count(self, obj):
        return obj.active_products_count
    products_count.short_description = 'عدد المنتجات'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'ordering', 'is_primary']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['sku', 'price', 'quantity', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'quantity', 'stock_status', 
                    'status', 'is_active', 'sales_count']
    list_filter = ['status', 'is_active', 'stock_status', 'product_type', 
                   'is_featured', 'is_bestseller']
    search_fields = ['name', 'sku', 'barcode', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'quantity', 'is_active']
    readonly_fields = ['uuid', 'views', 'sales_count', 'created_at', 'updated_at']
    filter_horizontal = ['categories']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('uuid', 'name', 'slug', 'sku', 'barcode', 'product_type')
        }),
        ('الوصف', {
            'fields': ('short_description', 'description')
        }),
        ('التصنيف', {
            'fields': ('categories', 'brand')
        }),
        ('الأسعار', {
            'fields': ('price', 'compare_price', 'cost_price', 'tax_rate')
        }),
        ('المخزون', {
            'fields': ('quantity', 'low_stock_threshold', 'manage_stock', 'stock_status')
        }),
        ('الأبعاد', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('الإعدادات', {
            'fields': ('status', 'is_active', 'is_featured', 'is_bestseller', 
                      'is_new', 'ordering')
        }),
        ('إحصائيات', {
            'fields': ('views', 'sales_count', 'wishlist_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'ordering']
    list_filter = ['is_primary', 'product']
    list_editable = ['ordering', 'is_primary']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    image_preview.short_description = 'معاينة'


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value', 'color']
    list_filter = ['attribute']
    search_fields = ['value']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'price', 'quantity', 'is_active']
    list_filter = ['is_active', 'product']
    search_fields = ['sku', 'product__name']
    filter_horizontal = ['attributes']
