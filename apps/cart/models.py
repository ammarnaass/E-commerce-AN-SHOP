from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from decimal import Decimal


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
                               on_delete=models.CASCADE, 
                               null=True, blank=True, 
                               related_name='cart',
                               verbose_name=_('المستخدم'))
    session_key = models.CharField(_('مفتاح الجلسة'), max_length=40, 
                                  null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('سلة التسوق')
        verbose_name_plural = _('سلال التسوق')
    
    def __str__(self):
        if self.user:
            return f"سلة {self.user.email}"
        return f"سلة الجلسة {self.session_key}"
    
    @staticmethod
    def get_or_create_cart(request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            session_cart = Cart.objects.filter(
                session_key=request.session.session_key
            ).first()
            if session_cart and session_cart != cart:
                cart.merge_with(session_cart)
                session_cart.delete()
        else:
            if not request.session.session_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(
                session_key=request.session.session_key
            )
        return cart
    
    def add_item(self, product, variant=None, quantity=1, override_quantity=False):
        from apps.store.models import Product, ProductVariant
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            if override_quantity:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            
            if cart_item.quantity <= 0:
                cart_item.delete()
                return False
            
            cart_item.save()
        
        self.save()
        return True
    
    def remove_item(self, product, variant=None):
        CartItem.objects.filter(
            cart=self,
            product=product,
            variant=variant
        ).delete()
        self.save()
    
    def clear(self):
        self.items.all().delete()
        self.save()
    
    def merge_with(self, other_cart):
        for item in other_cart.items.all():
            self.add_item(
                product=item.product,
                variant=item.variant,
                quantity=item.quantity
            )
    
    @property
    def items(self):
        return self.cart_items.select_related('product', 'variant').all()
    
    @property
    def count(self):
        return self.items.count()
    
    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items)
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items)
    
    @property
    def tax_total(self):
        return sum(item.tax_amount for item in self.items)
    
    @property
    def total(self):
        return self.subtotal + self.tax_total
    
    def get_summary(self):
        return {
            'count': self.count,
            'total_quantity': self.total_quantity,
            'subtotal': float(self.subtotal),
            'tax_total': float(self.tax_total),
            'total': float(self.total),
            'items': [
                {
                    'id': item.id,
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'variant_id': item.variant.id if item.variant else None,
                    'quantity': item.quantity,
                    'price': float(item.unit_price),
                    'total_price': float(item.total_price),
                }
                for item in self.items
            ]
        }


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, 
                            related_name='cart_items',
                            verbose_name=_('السلة'))
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE,
                               verbose_name=_('المنتج'))
    variant = models.ForeignKey('store.ProductVariant', on_delete=models.CASCADE, 
                               null=True, blank=True,
                               verbose_name=_('المتغير'))
    quantity = models.PositiveIntegerField(_('الكمية'), default=1)
    added_at = models.DateTimeField(_('تاريخ الإضافة'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('عنصر السلة')
        verbose_name_plural = _('عناصر السلة')
        unique_together = ['cart', 'product', 'variant']
    
    def __str__(self):
        variant_str = f" - {self.variant}" if self.variant else ""
        return f"{self.quantity} × {self.product.name}{variant_str}"
    
    @property
    def unit_price(self):
        if self.variant and self.variant.final_price:
            return self.variant.final_price
        return self.product.price
    
    @property
    def tax_rate(self):
        return self.product.tax_rate
    
    @property
    def tax_amount(self):
        return (self.unit_price * self.tax_rate / 100) * self.quantity
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity
    
    @property
    def total_with_tax(self):
        return self.total_price + self.tax_amount
    
    @property
    def available_quantity(self):
        if self.variant:
            return self.variant.quantity
        return self.product.quantity
    
    def is_available(self):
        return self.available_quantity >= self.quantity
