from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
import uuid


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(_('اسم الفئة'), max_length=100)
    slug = models.SlugField(_('رابط الفئة'), max_length=120, unique=True, blank=True)
    description = models.TextField(_('الوصف'), blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, 
                               null=True, blank=True, 
                               related_name='children',
                               verbose_name=_('الفئة الأم'))
    image = models.ImageField(_('الصورة'), upload_to='categories/', 
                              blank=True, null=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    ordering = models.IntegerField(_('الترتيب'), default=0)
    meta_title = models.CharField(_('عنوان Meta'), max_length=60, blank=True)
    meta_description = models.CharField(_('وصف Meta'), max_length=160, blank=True)
    
    class Meta:
        verbose_name = _('الفئة')
        verbose_name_plural = _('الفئات')
        ordering = ['ordering', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def active_products_count(self):
        return self.products.filter(is_active=True, status='published').count()


class Brand(TimeStampedModel):
    name = models.CharField(_('اسم الماركة'), max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(_('الشعار'), upload_to='brands/', blank=True, null=True)
    description = models.TextField(_('الوصف'), blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    
    class Meta:
        verbose_name = _('الماركة')
        verbose_name_plural = _('الماركات')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('مسودة')
        PUBLISHED = 'published', _('منشور')
        OUT_OF_STOCK = 'out_of_stock', _('نفذت الكمية')
        ARCHIVED = 'archived', _('مؤرشف')
    
    class ProductType(models.TextChoices):
        SIMPLE = 'simple', _('منتج بسيط')
        VARIABLE = 'variable', _('منتج متغير')
        DIGITAL = 'digital', _('منتج رقمي')
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(_('اسم المنتج'), max_length=200)
    slug = models.SlugField(_('رابط المنتج'), max_length=220, unique=True, blank=True)
    sku = models.CharField(_('كود المنتج'), max_length=50, unique=True, db_index=True)
    barcode = models.CharField(_('الباركود'), max_length=100, blank=True, db_index=True)
    
    description = models.TextField(_('الوصف الكامل'))
    short_description = models.TextField(_('الوصف المختصر'), max_length=500)
    
    product_type = models.CharField(_('نوع المنتج'), max_length=20, 
                                   choices=ProductType.choices, 
                                   default=ProductType.SIMPLE)
    
    categories = models.ManyToManyField(Category, related_name='products',
                                       verbose_name=_('الفئات'))
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='products',
                             verbose_name=_('الماركة'))
    
    price = models.DecimalField(_('السعر'), max_digits=12, decimal_places=2,
                               validators=[MinValueValidator(0)])
    compare_price = models.DecimalField(_('سعر المقارنة'), max_digits=12, 
                                       decimal_places=2, blank=True, null=True,
                                       validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(_('سعر التكلفة'), max_digits=12, 
                                    decimal_places=2, blank=True, null=True,
                                    validators=[MinValueValidator(0)])
    tax_rate = models.DecimalField(_('معدل الضريبة %'), max_digits=5, 
                                  decimal_places=2, default=15)
    
    quantity = models.IntegerField(_('الكمية المتاحة'), default=0)
    low_stock_threshold = models.IntegerField(_('حد المخزون المنخفض'), default=5)
    manage_stock = models.BooleanField(_('إدارة المخزون'), default=True)
    stock_status = models.CharField(_('حالة المخزون'), max_length=20,
                                   choices=[
                                       ('in_stock', _('متوفر')),
                                       ('low_stock', _('مخزون منخفض')),
                                       ('out_of_stock', _('غير متوفر'))
                                   ], default='in_stock')
    
    weight = models.DecimalField(_('الوزن (كجم)'), max_digits=8, 
                                decimal_places=3, blank=True, null=True)
    length = models.DecimalField(_('الطول (سم)'), max_digits=8, 
                                decimal_places=2, blank=True, null=True)
    width = models.DecimalField(_('العرض (سم)'), max_digits=8, 
                               decimal_places=2, blank=True, null=True)
    height = models.DecimalField(_('الارتفاع (سم)'), max_digits=8, 
                                decimal_places=2, blank=True, null=True)
    
    meta_title = models.CharField(_('عنوان Meta'), max_length=60, blank=True)
    meta_description = models.CharField(_('وصف Meta'), max_length=160, blank=True)
    meta_keywords = models.TextField(_('كلمات دلالية'), blank=True)
    
    views = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)
    sales_count = models.PositiveIntegerField(_('عدد المبيعات'), default=0)
    wishlist_count = models.PositiveIntegerField(_('في قائمة الرغبات'), default=0)
    
    status = models.CharField(_('الحالة'), max_length=20, 
                             choices=Status.choices, default=Status.DRAFT)
    is_active = models.BooleanField(_('نشط'), default=True)
    is_featured = models.BooleanField(_('مميز'), default=False)
    is_bestseller = models.BooleanField(_('الأكثر مبيعاً'), default=False)
    is_new = models.BooleanField(_('جديد'), default=False)
    ordering = models.IntegerField(_('الترتيب'), default=0)
    
    class Meta:
        verbose_name = _('المنتج')
        verbose_name_plural = _('المنتجات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku', 'barcode']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['-sales_count']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        
        if self.manage_stock:
            if self.quantity <= 0:
                self.stock_status = 'out_of_stock'
                self.status = self.Status.OUT_OF_STOCK
            elif self.quantity <= self.low_stock_threshold:
                self.stock_status = 'low_stock'
            else:
                self.stock_status = 'in_stock'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})
    
    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            discount = ((self.compare_price - self.price) / self.compare_price) * 100
            return round(discount, 1)
        return 0
    
    @property
    def price_with_tax(self):
        tax_amount = (self.price * self.tax_rate) / 100
        return self.price + tax_amount
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])
    
    def increment_sales(self, quantity=1):
        self.sales_count += quantity
        if self.manage_stock:
            self.quantity -= quantity
        self.save(update_fields=['sales_count', 'quantity'])
    
    def get_primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='images')
    image = models.ImageField(_('الصورة'), upload_to='products/images/')
    alt_text = models.CharField(_('النص البديل'), max_length=100, blank=True)
    ordering = models.IntegerField(_('الترتيب'), default=0)
    is_primary = models.BooleanField(_('الصورة الرئيسية'), default=False)
    
    class Meta:
        ordering = ['ordering', '-is_primary']
        verbose_name = _('صورة المنتج')
        verbose_name_plural = _('صور المنتجات')
    
    def __str__(self):
        return f"{self.product.name} - صورة #{self.id}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class Attribute(TimeStampedModel):
    name = models.CharField(_('اسم الخاصية'), max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    description = models.TextField(_('الوصف'), blank=True)
    
    class Meta:
        verbose_name = _('خاصية')
        verbose_name_plural = _('الخصائص')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class AttributeValue(TimeStampedModel):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, 
                                 related_name='values')
    value = models.CharField(_('القيمة'), max_length=100)
    color = models.CharField(_('لون (كود HEX)'), max_length=7, blank=True)
    
    class Meta:
        verbose_name = _('قيمة الخاصية')
        verbose_name_plural = _('قيم الخصائص')
        unique_together = ['attribute', 'value']
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='variants')
    sku = models.CharField(_('كود المتغير'), max_length=50, unique=True)
    attributes = models.ManyToManyField(AttributeValue, 
                                        verbose_name=_('الخصائص'))
    price = models.DecimalField(_('السعر'), max_digits=12, decimal_places=2, 
                               blank=True, null=True)
    compare_price = models.DecimalField(_('سعر المقارنة'), max_digits=12, 
                                       decimal_places=2, blank=True, null=True)
    quantity = models.IntegerField(_('الكمية'), default=0)
    weight = models.DecimalField(_('الوزن'), max_digits=8, decimal_places=3, 
                                blank=True, null=True)
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, 
                             null=True, blank=True, 
                             verbose_name=_('الصورة الخاصة'))
    is_active = models.BooleanField(_('نشط'), default=True)
    
    class Meta:
        verbose_name = _('متغير المنتج')
        verbose_name_plural = _('متغيرات المنتج')
    
    def __str__(self):
        attributes_str = ' | '.join([str(attr) for attr in self.attributes.all()])
        return f"{self.product.name} - {attributes_str}"
    
    @property
    def final_price(self):
        return self.price or self.product.price
    
    @property
    def final_compare_price(self):
        return self.compare_price or self.product.compare_price
