from django.core import signing
from django.utils import timezone
from datetime import date

# Daily QR signature token key
QR_SALT = 'payroll-attendance-qr-token'

def generate_daily_qr_token():
    """Generates a signed QR token for the current date. Valid for 1 day."""
    today_str = str(date.today())
    return signing.dumps({'date': today_str}, salt=QR_SALT)

def verify_qr_token(token):
    """Verifies the QR token. Returns True and date if valid, False otherwise."""
    try:
        # Max age of 18 hours (64800 seconds) to prevent old QR codes from being used
        data = signing.loads(token, salt=QR_SALT, max_age=64800)
        token_date_str = data.get('date')
        if token_date_str == str(date.today()):
            return True, token_date_str
        return False, None
    except signing.SignatureExpired:
        return False, "Expired"
    except signing.BadSignature:
        return False, "Invalid"
