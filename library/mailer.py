"""Notificaciones por correo (SMTP). Separado de helper_functions en el pase 2.

El host/puerto SMTP salen de MailConfig (claves opcionales `smtp_host` /
`smtp_port` en mail.email); antes 'smtp.gmail.com:465' estaba hardcodeado.

Funciones BLOQUEANTES (smtplib): llamar con asyncio.to_thread desde async.
"""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from classes.config import MailConfig
from library.security.key_manager import load_master_keys


def send_mail(recipient, subject, body, email_cfg=None):
    """
    Envía un correo usando SMTP seguro.
    :param recipient: Destinatario
    :param subject: Asunto
    :param body: Texto del correo
    :param email_cfg: Objeto MailConfig opcional. Si no, se carga al vuelo.
    """
    from library.logging_helpers import info

    if not email_cfg:
        key, hmac_key = load_master_keys()
        email_cfg = MailConfig(key=key, hmac_key=hmac_key)

    root_email = email_cfg.get_email()
    root_password = email_cfg.get_password()

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = root_email
    msg['To'] = recipient
    msg.set_content(body)

    with smtplib.SMTP_SSL(email_cfg.get_smtp_host(), email_cfg.get_smtp_port()) as smtp:
        smtp.login(root_email, root_password)
        smtp.send_message(msg)
    info(f"📧 Correo enviado a {recipient}")


def notify_error_mail(subject, body):
    """Envía `body` a todos los correos de config/emails.txt.

    Una única conexión SMTP_SSL + login para TODOS los destinatarios (antes,
    pese a lo que decía este docstring, send_mail abría un handshake TLS y un
    login por destinatario — segundos extra por alerta y riesgo de rate-limit
    de Gmail). Es BLOQUEANTE (SMTP): llamar con asyncio.to_thread desde async.
    """
    from library.file_explorer import load_mails
    from library.logging_helpers import error, info

    recipients = load_mails("config") or []
    if not recipients:
        return

    try:
        key, hmac_key = load_master_keys()
        email_cfg = MailConfig(key=key, hmac_key=hmac_key)
    except Exception as e:
        error(f"No se pudo cargar la configuración de correo: {e}")
        return

    root_email = email_cfg.get_email()
    try:
        with smtplib.SMTP_SSL(email_cfg.get_smtp_host(), email_cfg.get_smtp_port()) as smtp:
            smtp.login(root_email, email_cfg.get_password())
            for mail in recipients:
                try:
                    msg = EmailMessage()
                    msg['Subject'] = subject
                    msg['From'] = root_email
                    msg['To'] = mail
                    msg.set_content(body)
                    smtp.send_message(msg)
                    info(f"📧 Correo enviado a {mail}")
                except Exception as e:
                    error(f"No se pudo enviar correo a {mail}: {e}")
    except Exception as e:
        error(f"No se pudo conectar al SMTP para notificar: {e}")
