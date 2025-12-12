import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.payment.models import PaymentMethod

print("Creating initial payment methods...")

cash_on_delivery, created = PaymentMethod.objects.get_or_create(
    code='cash_on_delivery',
    defaults={
        'name': 'الدفع عند الاستلام',
        'type': PaymentMethod.PaymentType.CASH_ON_DELIVERY,
        'description': 'ادفع نقداً عند استلام الطلب',
        'is_active': True,
        'requires_online_payment': False,
        'ordering': 1,
    }
)
if created:
    print("✓ تم إنشاء طريقة الدفع عند الاستلام")
else:
    print("- طريقة الدفع عند الاستلام موجودة مسبقاً")

credit_card, created = PaymentMethod.objects.get_or_create(
    code='credit_card',
    defaults={
        'name': 'بطاقة ائتمان',
        'type': PaymentMethod.PaymentType.CREDIT_CARD,
        'description': 'الدفع عبر البطاقة الائتمانية',
        'is_active': True,
        'requires_online_payment': True,
        'ordering': 2,
    }
)
if created:
    print("✓ تم إنشاء طريقة الدفع بالبطاقة الائتمانية")
else:
    print("- طريقة الدفع بالبطاقة الائتمانية موجودة مسبقاً")

print("\nتم إنشاء البيانات الأولية بنجاح!")
