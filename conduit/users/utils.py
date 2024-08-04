from django.core.signing import BadSignature, TimestampSigner


def get_email_token(email: str) -> str:
    signer = TimestampSigner()
    email_token = signer.sign(email)
    return email_token


def retrieve_email_from_token(token: str) -> str:
    signer = TimestampSigner()
    try:
        email = signer.unsign(token, max_age=1000)
    except BadSignature:
        return None
    return email
