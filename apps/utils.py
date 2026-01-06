import datetime
import random
import re
from datetime import timedelta

from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.models import CustomAuthToken


def create_user_token(user, device=None, max_tokens=3):
    tokens = CustomAuthToken.objects.filter(user=user)
    if tokens.count() >= max_tokens:
        tokens.order_by('created').first().delete()

    token_instance, token = CustomAuthToken.objects.create(
        user=user,
        device=device,
        expiry=timedelta(days=10)
    )
    return token


def get_cache_key(email):
    return f"verify_code:{email}"


def get_limit_key(email):
    return f"verify_limit:{email}"


def send_verification_code(email, expired_time=300):
    limit_key = get_limit_key(email)
    last_sent = cache.get(limit_key)

    if last_sent:
        now = timezone.now()
        remaining = int((last_sent + datetime.timedelta(seconds=expired_time) - now).total_seconds())
        if remaining > 0:
            raise ValidationError({"message": f"Please wait {remaining} seconds before requesting a new code"})

    # 6 xonali kod
    code = random.randint(100000, 999999)
    print(code)
    # Cache-ga saqlash
    code_key = get_cache_key(email)
    cache.set(code_key, code, timeout=expired_time)

    cache.set(limit_key, timezone.now(), timeout=expired_time)

    # Gmailga yuborish
    subject = "Your Verification Code"
    message = f"Your verification code is: {code}"
    from_email = None  # DEFAULT_FROM_EMAIL ishlaydi

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[email],
        fail_silently=False
    )

    return code


def check_verification_code(email, code):
    code_key = get_cache_key(email)
    cached = cache.get(code_key)
    if cached is None:
        return False
    return cached == code

def normalize_phone(value):
    digits = re.findall(r'\d', value)
    if len(digits) != 12:
        raise ValidationError('Phone number must be at least 9 digits')
    return ''.join(digits)