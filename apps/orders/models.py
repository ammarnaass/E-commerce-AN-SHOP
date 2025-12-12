from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator
import uuid
from decimal import Decimal


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('قيد الانتظار')
        CONFIRMED = 'confirmed', _('مؤكد')
        PROCESSING = 'processing', _('قيد المعالجة')
        SHIPPED = 'shipped', _('تم الشحن')
        DELIVERED = 'delivered', _('تم التوصيل')
        CANCELLED = 'cancelled', _('ملغي')
        REFUNDED = 'refunded', _('مسترد')
    
    class OrderType(models.TextChoices):
        REGULAR = 'regular', _('طلب عادي')
        QUICK_ORDER = 'quick_order', _('طلب سريع')
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order_number = models.CharField(_('رقم الطلب'), max_length=50, unique=True, 
                                   db_index=True, editable=False)
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='orders',
                                verbose_name=_('العميل'))
    customer_name = models.CharField(_('اسم العميل'), max_length=100)
    customer_email = models.EmailField(_('البريد الإلكتروني'), blank=True)
    customer_phone = models.CharField(_('رقم الهاتف'), max_length=17)
    
    order_type = models.CharField(_('نوع الطلب'), max_length=20,
                                 choices=OrderType.choices,
                                 default=OrderType.REGULAR)
    
    shipping_country = models.CharField(_('الدولة'), max_length=100, 
                                       default='Saudi Arabia')
    shipping_city = models.CharField(_('المدينة'), max_length=100)
    shipping_district = models.CharField(_('الحي'), max_length=100, blank=True)
    shipping_address = models.TextField(_('العنوان التفصيلي'))
    shipping_building_number = models.CharField(_('رقم المبنى'), max_length=50, 
                                               blank=True)
    shipping_postal_code = models.CharField(_('الرمز البريدي'), max_length=20, 
                                           blank=True)
    
    subtotal = models.DecimalField(_('المجموع الفرعي'), max_digits=12, 
                                  decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('الضريبة'), max_digits=12, 
                                    decimal_places=2, default=0)
    shipping_cost = models.DecimalField(_('تكلفة الشحن'), max_digits=10, 
                                       decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('الخصم'), max_digits=10, 
                                         decimal_places=2, default=0)
    total = models.DecimalField(_('المجموع الكلي'), max_digits=12, 
                               decimal_places=2, default=0)
    
    payment_method = models.ForeignKey('payment.PaymentMethod', 
                                      on_delete=models.PROTECT,
                                      verbose_name=_('طريقة الدفع'))
    payment_status = models.BooleanField(_('حالة الدفع'), default=False)
    
    status = models.CharField(_('حالة الطلب'), max_length=20,
                            choices=Status.choices, default=Status.PENDING)
    
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    confirmed_at = models.DateTimeField(_('تاريخ التأكيد'), null=True, blank=True)
    shipped_at = models.DateTimeField(_('تاريخ الشحن'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('تاريخ التوصيل'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('الطلب')
        verbose_name_plural = _('الطلبات')
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"طلب #{self.order_number}"
    
    def calculate_totals(self):
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.tax_amount = sum(item.tax_amount for item in self.items.all())
        self.total = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, 
                             related_name='items',
                             verbose_name=_('الطلب'))
    product = models.ForeignKey('store.Product', on_delete=models.PROTECT,
                               verbose_name=_('المنتج'))
    variant = models.ForeignKey('store.ProductVariant', on_delete=models.PROTECT,
                               null=True, blank=True,
                               verbose_name=_('المتغير'))
    
    product_name = models.CharField(_('اسم المنتج'), max_length=200)
    product_sku = models.CharField(_('كود المنتج'), max_length=50)
    
    price = models.DecimalField(_('السعر'), max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(_('الكمية'), default=1)
    tax_rate = models.DecimalField(_('معدل الضريبة'), max_digits=5, 
                                  decimal_places=2, default=15)
    
    class Meta:
        verbose_name = _('عنصر الطلب')
        verbose_name_plural = _('عناصر الطلب')
    
    def __str__(self):
        return f"{self.quantity} × {self.product_name}"
    
    @property
    def total_price(self):
        return self.price * self.quantity
    
    @property
    def tax_amount(self):
        return (self.price * self.tax_rate / 100) * self.quantity
    
    @property
    def total_with_tax(self):
        return self.total_price + self.tax_amount


class QuickOrder(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', _('قيد الانتظار')
        CONFIRMED = 'confirmed', _('مؤكد')
        PROCESSING = 'processing', _('قيد المعالجة')
        CANCELLED = 'cancelled', _('ملغي')
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("رقم الهاتف يجب أن يكون بتنسيق: '+999999999'. يسمح حتى 15 رقمًا.")
    )
    
    phone_number = models.CharField(_('رقم الهاتف'), validators=[phone_regex], 
                                   max_length=17, db_index=True)
    name = models.CharField(_('الاسم'), max_length=100)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True)
    
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE,
                              verbose_name=_('المنتج'))
    variant = models.ForeignKey('store.ProductVariant', on_delete=models.SET_NULL,
                              null=True, blank=True, verbose_name=_('المتغير'))
    quantity = models.PositiveIntegerField(_('الكمية'), default=1)
    
    city = models.CharField(_('المدينة'), max_length=100)
    district = models.CharField(_('الحي'), max_length=100, blank=True)
    address = models.TextField(_('العنوان التفصيلي'), blank=True)
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    status = models.CharField(_('الحالة'), max_length=20,
                            choices=OrderStatus.choices,
                            default=OrderStatus.PENDING)
    
    ip_address = models.GenericIPAddressField(_('عنوان IP'), blank=True, null=True)
    user_agent = models.TextField(_('معلومات المتصفح'), blank=True)
    
    confirmed_at = models.DateTimeField(_('تاريخ التأكيد'), null=True, blank=True)
    processed_at = models.DateTimeField(_('تاريخ المعالجة'), null=True, blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('طلب سريع')
        verbose_name_plural = _('الطلبات السريعة')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"طلب سريع #{self.id} - {self.name}"
