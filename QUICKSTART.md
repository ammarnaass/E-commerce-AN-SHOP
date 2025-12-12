# دليل البدء السريع - متجر إلكتروني

## متطلبات النظام

- Python 3.10 أو أحدث
- pip (مدير الحزم)
- SQLite (يأتي مع Python)

## التثبيت والتشغيل

### 1. إنشاء بيئة افتراضية

```bash
python -m venv venv
```

### 2. تفعيل البيئة الافتراضية

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. تثبيت المتطلبات

```bash
pip install -r requirements/base.txt
pip install django-debug-toolbar
```

### 4. تطبيق الترحيلات

```bash
export DJANGO_SETTINGS_MODULE=config.settings.development  # Linux/Mac
set DJANGO_SETTINGS_MODULE=config.settings.development     # Windows

python manage.py migrate
```

### 5. إنشاء مستخدم فائق

```bash
python -c "from apps.accounts.models import User; User.objects.create_superuser('admin@store.com', 'admin123456', first_name='Admin', last_name='User')"
```

أو بشكل تفاعلي:
```bash
python manage.py shell
>>> from apps.accounts.models import User
>>> User.objects.create_superuser('admin@store.com', 'your_password', first_name='Admin', last_name='User')
>>> exit()
```

### 6. إنشاء البيانات الأولية (اختياري)

```bash
python create_initial_data.py
```

### 7. تشغيل الخادم

```bash
python manage.py runserver
```

الآن يمكنك زيارة:
- **الموقع الرئيسي:** http://localhost:8000
- **لوحة الإدارة:** http://localhost:8000/admin

## بيانات الدخول للوحة الإدارة

- **البريد الإلكتروني:** admin@store.com
- **كلمة المرور:** admin123456

## الميزات المتاحة

### لوحة الإدارة (Admin)

1. **إدارة المستخدمين**
   - إضافة وتعديل المستخدمين
   - إدارة الصلاحيات
   - إدارة العناوين

2. **إدارة المتجر**
   - الفئات (Categories)
   - الماركات (Brands)
   - المنتجات (Products)
   - صور المنتجات
   - الخصائص والمتغيرات

3. **إدارة الطلبات**
   - الطلبات العادية
   - الطلبات السريعة
   - تتبع حالة الطلب

4. **إدارة الدفع**
   - طرق الدفع
   - سجل المدفوعات

5. **سلة التسوق**
   - عرض جميع السلات
   - إدارة عناصر السلة

## إضافة منتجات للاختبار

### عبر لوحة الإدارة

1. اذهب إلى http://localhost:8000/admin
2. سجل الدخول باستخدام بيانات المستخدم الفائق
3. انتقل إلى "Store" > "Categories" وأضف فئات
4. انتقل إلى "Store" > "Brands" وأضف ماركات (اختياري)
5. انتقل إلى "Store" > "Products" وأضف منتجات:
   - املأ الحقول المطلوبة
   - اختر الفئة
   - حدد السعر والكمية
   - ارفع الصور
   - احفظ المنتج

### عبر shell Django

```bash
python manage.py shell
```

```python
from apps.store.models import Category, Product
from decimal import Decimal

# إنشاء فئة
category = Category.objects.create(
    name='إلكترونيات',
    is_active=True
)

# إنشاء منتج
product = Product.objects.create(
    name='هاتف ذكي',
    sku='PHONE-001',
    description='هاتف ذكي متطور بمواصفات عالية',
    short_description='هاتف ذكي عالي الجودة',
    price=Decimal('2999.00'),
    quantity=50,
    status='published',
    is_active=True
)

# إضافة الفئة للمنتج
product.categories.add(category)

print(f"تم إنشاء المنتج: {product.name}")
```

## التطوير

### تشغيل الاختبارات

```bash
python manage.py test
```

### إنشاء migration جديد

```bash
python manage.py makemigrations
```

### إنشاء تطبيق جديد

```bash
cd apps
django-admin startapp app_name
```

لا تنس إضافة التطبيق الجديد إلى `INSTALLED_APPS` في `config/settings/base.py`:

```python
INSTALLED_APPS = [
    # ...
    'apps.app_name',
]
```

## استكشاف الأخطاء

### مشكلة: Module not found

**الحل:**
```bash
pip install -r requirements/base.txt
```

### مشكلة: No such table

**الحل:**
```bash
python manage.py migrate
```

### مشكلة: Port already in use

**الحل:** استخدم منفذ مختلف
```bash
python manage.py runserver 8001
```

## المساعدة والدعم

للمزيد من المعلومات، راجع:
- [README.md](README.md) - التوثيق الكامل
- [Django Documentation](https://docs.djangoproject.com/)

## إيقاف الخادم

اضغط `Ctrl+C` في الطرفية لإيقاف خادم التطوير.

## إلغاء تفعيل البيئة الافتراضية

```bash
deactivate
```

---

🎉 مبروك! لقد نجحت في إعداد المتجر الإلكتروني!
