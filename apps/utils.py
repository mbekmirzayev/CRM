import datetime
import random
import re
from datetime import timedelta

from django.core.cache import cache
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


def get_cache_key(phone):
    return f"verify_code:{phone}"


def get_limit_key(phone):
    return f"verify_limit:{phone}"


def send_verification_code(phone, expired_time=300):
    limit_key = get_limit_key(phone)
    last_sent = cache.get(limit_key)

    if last_sent:
        now = timezone.now()
        remaining = int((last_sent + datetime.timedelta(seconds=expired_time) - now).total_seconds())
        if remaining > 0:
            raise ValidationError({"message": f"Please wait {remaining} seconds before requesting a new code"})

    code = random.randint(100000, 999999)
    print(f"OTP => {code}")
    code_key = get_cache_key(phone)
    cache.set(code_key, code, timeout=expired_time)

    cache.set(limit_key, timezone.now(), timeout=expired_time)


def check_verification_code(phone, code):
    code_key = get_cache_key(phone)
    cached = cache.get(code_key)
    if cached is None:
        return False
    return cached == code


def normalize_phone(value):
    digits = re.findall(r'\d', value)
    if len(digits) != 12:
        raise ValidationError('Phone number must be at least 9 digits')
    return ''.join(digits)
