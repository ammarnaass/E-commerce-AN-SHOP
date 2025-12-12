from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class PaymentMethod(models.Model):
    class PaymentType(models.TextChoices):
        CASH_ON_DELIVERY = 'cod', _('الدفع عند الاستلام')
        CREDIT_CARD = 'credit_card', _('بطاقة ائتمان')
        BANK_TRANSFER = 'bank_transfer', _('تحويل بنكي')
        WALLET = 'wallet', _('محفظة إلكترونية')
    
    name = models.CharField(_('الاسم'), max_length=100)
    code = models.CharField(_('الكود'), max_length=50, unique=True)
    type = models.CharField(_('النوع'), max_length=20, choices=PaymentType.choices)
    is_active = models.BooleanField(_('نشط'), default=True)
    description = models.TextField(_('الوصف'), blank=True)
    instructions = models.TextField(_('التعليمات'), blank=True)
    icon = models.CharField(_('الأيقونة'), max_length=50, blank=True)
    ordering = models.IntegerField(_('الترتيب'), default=0)
    
    requires_online_payment = models.BooleanField(_('يتطلب دفع إلكتروني'), 
                                                  default=False)
    extra_fee = models.DecimalField(_('رسوم إضافية'), max_digits=10, 
                                   decimal_places=2, default=0)
    min_order_amount = models.DecimalField(_('الحد الأدنى للطلب'), 
                                          max_digits=10, decimal_places=2, 
                                          default=0)
    max_order_amount = models.DecimalField(_('الحد الأقصى للطلب'), 
                                          max_digits=10, decimal_places=2, 
                                          null=True, blank=True)
    
    class Meta:
        verbose_name = _('طريقة الدفع')
        verbose_name_plural = _('طرق الدفع')
        ordering = ['ordering', 'name']
    
    def __str__(self):
        return self.name
    
    def is_available_for_order(self, order_amount):
        if not self.is_active:
            return False
        
        if order_amount < self.min_order_amount:
            return False
        
        if self.max_order_amount and order_amount > self.max_order_amount:
            return False
        
        return True


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('قيد الانتظار')
        PROCESSING = 'processing', _('قيد المعالجة')
        AUTHORIZED = 'authorized', _('مصرح به')
        CAPTURED = 'captured', _('تم التحصيل')
        PARTIALLY_REFUNDED = 'partially_refunded', _('مسترد جزئياً')
        REFUNDED = 'refunded', _('مسترد')
        FAILED = 'failed', _('فشل')
        CANCELLED = 'cancelled', _('ملغي')
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, 
                                related_name='payment',
                                verbose_name=_('الطلب'))
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT,
                                      related_name='payments',
                                      verbose_name=_('طريقة الدفع'))
    
    amount = models.DecimalField(_('المبلغ'), max_digits=12, decimal_places=2,
                               validators=[MinValueValidator(0)])
    currency = models.CharField(_('العملة'), max_length=3, default='SAR')
    status = models.CharField(_('الحالة'), max_length=20,
                            choices=PaymentStatus.choices,
                            default=PaymentStatus.PENDING)
    
    transaction_id = models.CharField(_('رقم المعاملة'), max_length=100, 
                                     blank=True, db_index=True)
    gateway_response = models.JSONField(_('رد بوابة الدفع'), blank=True, null=True)
    
    authorized_at = models.DateTimeField(_('تاريخ التصريح'), null=True, blank=True)
    captured_at = models.DateTimeField(_('تاريخ التحصيل'), null=True, blank=True)
    
    receipt_file = models.FileField(_('إيصال الدفع'), 
                                   upload_to='payments/receipts/',
                                   blank=True, null=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('دفعة')
        verbose_name_plural = _('الدفعات')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"دفعة #{self.id} - {self.amount} {self.currency}"
    
    def mark_as_paid(self, transaction_id='', gateway_response=None):
        from apps.orders.models import Order
        
        self.status = self.PaymentStatus.CAPTURED
        self.transaction_id = transaction_id
        self.gateway_response = gateway_response or {}
        self.captured_at = timezone.now()
        self.save()
        
        self.order.status = Order.Status.CONFIRMED
        self.order.payment_status = True
        self.order.save()
    
    def can_refund(self):
        return self.status in [
            self.PaymentStatus.CAPTURED,
            self.PaymentStatus.PARTIALLY_REFUNDED
        ]
