from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('يجب إدخال البريد الإلكتروني'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('يجب أن يكون المستخدم الفائق is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('يجب أن يكون المستخدم الفائق is_superuser=True'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("رقم الهاتف يجب أن يكون بتنسيق: '+999999999'. يسمح حتى 15 رقمًا.")
    )
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(_('البريد الإلكتروني'), unique=True, db_index=True)
    first_name = models.CharField(_('الاسم الأول'), max_length=50)
    last_name = models.CharField(_('اسم العائلة'), max_length=50)
    phone_number = models.CharField(_('رقم الهاتف'), validators=[phone_regex], 
                                   max_length=17, blank=True)
    
    profile_image = models.ImageField(_('الصورة الشخصية'), 
                                     upload_to='users/profiles/', 
                                     blank=True, null=True)
    
    date_of_birth = models.DateField(_('تاريخ الميلاد'), blank=True, null=True)
    
    is_staff = models.BooleanField(_('موظف'), default=False)
    is_active = models.BooleanField(_('نشط'), default=True)
    is_customer = models.BooleanField(_('عميل'), default=True)
    
    date_joined = models.DateTimeField(_('تاريخ التسجيل'), auto_now_add=True)
    last_login = models.DateTimeField(_('آخر تسجيل دخول'), auto_now=True)
    
    email_verified = models.BooleanField(_('البريد الإلكتروني موثق'), default=False)
    phone_verified = models.BooleanField(_('رقم الهاتف موثق'), default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('المستخدم')
        verbose_name_plural = _('المستخدمون')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name


class Address(models.Model):
    class AddressType(models.TextChoices):
        SHIPPING = 'shipping', _('عنوان الشحن')
        BILLING = 'billing', _('عنوان الفواتير')
        BOTH = 'both', _('كلاهما')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                            related_name='addresses',
                            verbose_name=_('المستخدم'))
    
    address_type = models.CharField(_('نوع العنوان'), max_length=20, 
                                   choices=AddressType.choices,
                                   default=AddressType.SHIPPING)
    
    full_name = models.CharField(_('الاسم الكامل'), max_length=100)
    phone_number = models.CharField(_('رقم الهاتف'), max_length=17)
    
    country = models.CharField(_('الدولة'), max_length=100, default='Saudi Arabia')
    city = models.CharField(_('المدينة'), max_length=100)
    district = models.CharField(_('الحي'), max_length=100, blank=True)
    street_address = models.CharField(_('العنوان'), max_length=255)
    building_number = models.CharField(_('رقم المبنى'), max_length=50, blank=True)
    postal_code = models.CharField(_('الرمز البريدي'), max_length=20, blank=True)
    
    is_default = models.BooleanField(_('العنوان الافتراضي'), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('العنوان')
        verbose_name_plural = _('العناوين')
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.district}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)
