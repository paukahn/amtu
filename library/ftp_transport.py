"""Envío de ficheros por FTP/FTPS/SFTP (mecánica de red, sin configuración).

Separado de classes.config.FTPTransport en el pase 2: FTPConfig parsea y
guarda la configuración; este módulo solo sabe enviar. Corrige además la fuga
de paramiko.Transport: el close() original no estaba en finally, así que una
excepción en sftp.put dejaba la conexión abierta.

Pase 3 — verificación del host SFTP:
- Si la cuenta define `host_key` (huella SHA256 de la clave pública del
  servidor, formato OpenSSH `SHA256:xxxx…` o solo el base64), la clave del
  servidor se verifica ANTES de enviar la contraseña; si no coincide, se
  aborta (posible MITM). Sin `host_key` se envía igual, pero se avisa en el
  log con la huella observada para que el operador la fije en la config.
- Nuevo modo `ftps` (FTP explícito sobre TLS con protección del canal de
  datos) para destinos que no ofrecen SFTP; `ftp` plano se mantiene por
  compatibilidad, pero con aviso.

Obtener la huella del servidor (en el servidor o desde una máquina de
confianza):  ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub

Funciones BLOQUEANTES: llamar con asyncio.to_thread desde código async.
"""

from __future__ import annotations

import base64
import ftplib
import hashlib
import os

import paramiko

DEFAULT_TIMEOUT = 30


def send_file(cfg: dict, local_path: str) -> bool:
    """Envía `local_path` según `cfg` (host/username/password/folder_in/port/ftp_mode/host_key)."""
    mode = (cfg.get("ftp_mode") or "ftp").lower()
    if mode == "sftp":
        return _send_sftp(local_path, cfg)
    if mode == "ftps":
        return _send_ftp(local_path, cfg, tls=True)
    return _send_ftp(local_path, cfg, tls=False)


def _send_ftp(local_path: str, cfg: dict, *, tls: bool) -> bool:
    from library.logging_helpers import error

    ftp = ftplib.FTP_TLS() if tls else ftplib.FTP()
    if not tls:
        error(
            f"Transporte FTP SIN cifrar hacia {cfg.get('host')}: credenciales y datos viajan "
            "en claro. Considera ftp_mode = sftp o ftps.",
            type="warning",
        )
    with ftp:
        ftp.connect(cfg["host"], int(cfg.get("port") or 21), timeout=DEFAULT_TIMEOUT)
        ftp.login(cfg["username"], cfg["password"])
        if tls:
            ftp.prot_p()  # proteger también el canal de datos
        ftp.set_pasv(True)
        if cfg.get("folder_in"):
            ftp.cwd(cfg["folder_in"])
        with open(local_path, "rb") as f:
            ftp.storbinary(f"STOR {os.path.basename(local_path)}", f)
    return True


def _sha256_fingerprint(key) -> str:
    """Huella estilo OpenSSH: SHA256:<base64 sin '='>."""
    digest = hashlib.sha256(key.asbytes()).digest()
    return "SHA256:" + base64.b64encode(digest).decode("ascii").rstrip("=")


def _normalize_fp(value: str) -> str:
    value = (value or "").strip()
    if value.upper().startswith("SHA256:"):
        value = value[7:]
    return value.rstrip("=")


def _verify_host_key(transport: paramiko.Transport, cfg: dict) -> None:
    """Compara la clave del servidor con `host_key` de la config.

    Se ejecuta tras el intercambio de claves y ANTES de autenticar: si el
    servidor no es quien dice ser, la contraseña nunca llega a enviarse.
    """
    from library.logging_helpers import error

    server_key = transport.get_remote_server_key()
    observed = _sha256_fingerprint(server_key)
    expected = cfg.get("host_key")
    if not expected:
        error(
            f"SFTP {cfg.get('host')}: sin 'host_key' en la configuración — el servidor NO se "
            f"verifica (riesgo MITM). Huella observada: {observed} "
            f"(añádela con la CLI para fijarla).",
            type="warning",
        )
        return
    if _normalize_fp(expected) != _normalize_fp(observed):
        raise RuntimeError(
            f"Huella del host SFTP {cfg.get('host')} NO coincide: esperada {expected}, "
            f"observada {observed}. Posible MITM o cambio de clave del servidor; envío abortado."
        )


def _send_sftp(local_path: str, cfg: dict) -> bool:
    port = int(cfg.get("port") or 22)
    transport = paramiko.Transport((cfg["host"], port))
    try:
        # start_client hace el handshake SIN credenciales: primero verificar
        # el host, después autenticar.
        transport.start_client(timeout=DEFAULT_TIMEOUT)
        _verify_host_key(transport, cfg)
        transport.auth_password(cfg["username"], cfg["password"])
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            remote_dir = cfg.get("folder_in") or ""
            remote_path = os.path.join(remote_dir, os.path.basename(local_path)).replace("\\", "/")
            sftp.put(local_path, remote_path)
    finally:
        transport.close()
    return True
