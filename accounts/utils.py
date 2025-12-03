from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = request.build_absolute_uri(f"/accounts/verify/{uid}/{token}/")

    # Message texte
    message_txt = render_to_string("accounts/email_verify.txt", {
        "user": user,
        "site_name": settings.SITE_NAME,
        "verify_url": verify_url
    })

    # Message HTML (optionnel, sinon tu peux ignorer)
    message_html = render_to_string("accounts/email_verify.html", {
        "user": user,
        "site_name": settings.SITE_NAME,
        "verify_url": verify_url
    })

    email = EmailMessage(
        subject=f"Vérification de votre compte {settings.SITE_NAME}",
        body=message_txt,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.content_subtype = "plain"  # "html" si tu veux envoyer HTML
    email.send(fail_silently=False)
