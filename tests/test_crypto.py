"""Testes do módulo de integridade/autenticidade (Req #2: hash + certificado digital)."""
from sentinelia import crypto


def test_sha256_valor_conhecido():
    # SHA-256 oficial de b"abc"
    esperado = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert crypto.sha256_bytes(b"abc") == esperado


def test_hash_muda_com_um_byte():
    assert crypto.sha256_bytes(b"abc") != crypto.sha256_bytes(b"abd")


def test_assinatura_roundtrip_valida():
    priv, pub = crypto.generate_keypair()
    data = b"lote de focos integro"
    sig = crypto.sign(data, priv)
    assert crypto.verify_signature(data, sig, pub) is True


def test_adulteracao_de_dado_e_detectada():
    priv, pub = crypto.generate_keypair()
    original = b"foco: lat -3.5 lon -52.0 frp 250 risco alto"
    sig = crypto.sign(original, priv)
    # atacante esconde a queimada baixando o FRP -> 1 trecho alterado
    adulterado = b"foco: lat -3.5 lon -52.0 frp 010 risco baixo"
    assert crypto.verify_signature(adulterado, sig, pub) is False


def test_assinatura_corrompida_e_detectada():
    priv, pub = crypto.generate_keypair()
    data = b"modelo.pkl"
    sig = bytearray(crypto.sign(data, priv))
    sig[0] ^= 0x01  # corrompe 1 bit da assinatura
    assert crypto.verify_signature(data, bytes(sig), pub) is False


def test_certificado_digital_assina_e_verifica():
    cert_pem, key_pem = crypto.generate_self_signed_cert("SentinelIA")
    data = b"conteudo do modelo de risco"
    sig = crypto.sign(data, key_pem)
    pub = crypto.cert_public_key_pem(cert_pem)
    assert crypto.verify_signature(data, sig, pub) is True


def test_ensure_keypair_persiste(tmp_path):
    p1 = crypto.ensure_keypair(tmp_path / "keys")
    p2 = crypto.ensure_keypair(tmp_path / "keys")
    assert p1 == p2  # segunda chamada reusa as mesmas chaves
    assert (tmp_path / "keys" / "private_key.pem").exists()
