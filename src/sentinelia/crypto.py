"""Primitivas de integridade e autenticidade.

Implementa os conteúdos estudados **hash** e **certificado digital**:

- `sha256_*`  -> integridade (detecta adulteração de 1 bit).
- `sign` / `verify_signature` -> autenticidade + integridade (assinatura digital RSA-PSS).
- `generate_self_signed_cert` -> certificado digital X.509 (vincula identidade à chave pública).

É a base do Requisito #2 (proteção contra manipulação de dados e modelos em trânsito).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
from pathlib import Path
from typing import Tuple

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

# --------------------------------------------------------------------------- #
# Hash (integridade)
# --------------------------------------------------------------------------- #


def sha256_bytes(data: bytes) -> str:
    """Digest SHA-256 (hex) de um bloco de bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Digest SHA-256 (hex) de um arquivo, lido em blocos."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# Assinatura digital (autenticidade + integridade)
# --------------------------------------------------------------------------- #


def generate_keypair(key_size: int = 2048) -> Tuple[bytes, bytes]:
    """Gera um par de chaves RSA e retorna (private_pem, public_pem)."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def sign(data: bytes, private_pem: bytes) -> bytes:
    """Assina `data` com a chave privada (RSA-PSS + SHA-256)."""
    key = serialization.load_pem_private_key(private_pem, password=None)
    return key.sign(
        data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )


def verify_signature(data: bytes, signature: bytes, public_pem: bytes) -> bool:
    """Verifica a assinatura. Retorna False se dados OU assinatura foram alterados."""
    pub = serialization.load_pem_public_key(public_pem)
    try:
        pub.verify(
            signature,
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


# --------------------------------------------------------------------------- #
# Certificado digital X.509
# --------------------------------------------------------------------------- #


def generate_self_signed_cert(common_name: str = "SentinelIA") -> Tuple[bytes, bytes]:
    """Gera um certificado digital X.509 autoassinado e retorna (cert_pem, key_pem)."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SentinelIA - Nova Economia Espacial"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
        ]
    )
    now = _dt.datetime.now(_dt.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + _dt.timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return cert_pem, key_pem


def cert_public_key_pem(cert_pem: bytes) -> bytes:
    """Extrai a chave pública (PEM) de um certificado X.509."""
    cert = x509.load_pem_x509_certificate(cert_pem)
    return cert.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


# --------------------------------------------------------------------------- #
# Persistência de chaves
# --------------------------------------------------------------------------- #


def save_keypair(directory: str | Path, private_pem: bytes, public_pem: bytes) -> None:
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    (d / "private_key.pem").write_bytes(private_pem)
    (d / "public_key.pem").write_bytes(public_pem)


def ensure_keypair(directory: str | Path) -> Tuple[bytes, bytes]:
    """Carrega o par de chaves do diretório; gera e persiste se não existir."""
    d = Path(directory)
    priv = d / "private_key.pem"
    pub = d / "public_key.pem"
    if priv.exists() and pub.exists():
        return priv.read_bytes(), pub.read_bytes()
    private_pem, public_pem = generate_keypair()
    save_keypair(d, private_pem, public_pem)
    return private_pem, public_pem
