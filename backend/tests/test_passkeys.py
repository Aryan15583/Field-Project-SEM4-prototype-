"""Passkeys, tested end to end with a software authenticator (real P-256 keys and signatures)."""
import hashlib
import json
import struct

import cbor2
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy import select
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url

from app.db import SessionLocal
from app.models import AuditLog, Passkey, User, WebAuthnChallenge

from .conftest import enroll

RP_ID, ORIGIN = "testserver", "http://testserver"
UP, UV, AT = 0x01, 0x04, 0x40


class SoftKey:
    """Just enough of a platform authenticator: one discoverable ES256 credential."""

    def __init__(self, cred_id: bytes = b"cred-1-" + bytes(9)):
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.cred_id = cred_id
        self.count = 0
        self.user_handle = None

    def _client_data(self, kind, challenge, origin=ORIGIN):
        return json.dumps({"type": kind, "challenge": challenge, "origin": origin, "crossOrigin": False}).encode()

    def create(self, options, *, origin=ORIGIN, flags=UP | UV | AT):
        self.user_handle = options["user"]["id"]
        nums = self.key.public_key().public_numbers()
        cose = cbor2.dumps({1: 2, 3: -7, -1: 1, -2: nums.x.to_bytes(32, "big"), -3: nums.y.to_bytes(32, "big")})
        auth = (
            hashlib.sha256(options["rp"]["id"].encode()).digest() + bytes([flags]) + struct.pack(">I", self.count)
            + bytes(16) + struct.pack(">H", len(self.cred_id)) + self.cred_id + cose
        )
        att = cbor2.dumps({"fmt": "none", "attStmt": {}, "authData": auth})
        cid = bytes_to_base64url(self.cred_id)
        return {
            "id": cid, "rawId": cid, "type": "public-key",
            "response": {
                "clientDataJSON": bytes_to_base64url(self._client_data("webauthn.create", options["challenge"], origin)),
                "attestationObject": bytes_to_base64url(att),
                "transports": ["internal", "bogus"],
            },
        }

    def get(self, options, *, origin=ORIGIN, flags=UP | UV, key=None):
        self.count += 1
        auth = hashlib.sha256(options["rpId"].encode()).digest() + bytes([flags]) + struct.pack(">I", self.count)
        cdj = self._client_data("webauthn.get", options["challenge"], origin)
        sig = (key or self.key).sign(auth + hashlib.sha256(cdj).digest(), ec.ECDSA(hashes.SHA256()))
        cid = bytes_to_base64url(self.cred_id)
        return {
            "id": cid, "rawId": cid, "type": "public-key",
            "response": {
                "clientDataJSON": bytes_to_base64url(cdj),
                "authenticatorData": bytes_to_base64url(auth),
                "signature": bytes_to_base64url(sig),
                "userHandle": self.user_handle,
            },
        }


def _add_passkey(client, key, name="My laptop"):
    opts = client.post("/api/auth/passkeys/register/options").json()
    assert opts["rp"]["id"] == RP_ID and opts["authenticatorSelection"]["userVerification"] == "required"
    assert opts["authenticatorSelection"]["residentKey"] == "required"
    return client.post("/api/auth/passkeys/register", json={"credential": key.create(opts), "name": name})


def _sign_out(client):
    client.post("/api/auth/logout")
    client.cookies.clear()
    client.get("/api/auth/csrf")
    assert client.get("/api/auth/me").status_code == 401


def test_add_passkey_then_sign_in_without_a_code(client):
    enroll(client)
    key = SoftKey()
    r = _add_passkey(client, key)
    assert r.status_code == 200, r.text
    assert r.json()["name"] == "My laptop" and r.json()["last_used_at"] is None
    assert [p["name"] for p in client.get("/api/auth/passkeys").json()] == ["My laptop"]
    with SessionLocal() as db:
        pk = db.scalar(select(Passkey))
        assert pk.transports == ["internal"]  # unknown values dropped
        # the authenticator gets an opaque handle - not the email or the database id
        assert base64url_to_bytes(key.user_handle) not in (b"1", b"learner@example.com")

    _sign_out(client)
    opts = client.post("/api/auth/passkeys/login/options").json()
    assert opts["rpId"] == RP_ID and opts["userVerification"] == "required" and not opts.get("allowCredentials")
    r = client.post("/api/auth/passkeys/login", json={"credential": key.get(opts)})
    assert r.status_code == 200, r.text
    assert r.json()["user"]["email"] == "learner@example.com"
    assert client.get("/api/auth/me").status_code == 200  # fully signed in - no emailed code needed
    assert client.get("/api/auth/passkeys").json()[0]["last_used_at"] is not None
    with SessionLocal() as db:
        assert db.scalar(select(Passkey.sign_count)) == 1
        assert db.scalar(select(AuditLog.id).where(AuditLog.event == "login_passkey")) is not None
        assert db.scalars(select(WebAuthnChallenge)).all() == []  # used challenges are gone


def test_challenges_are_single_use_and_bound_to_the_flow(client):
    enroll(client)
    key = SoftKey()
    assert _add_passkey(client, key).status_code == 200
    _sign_out(client)

    opts = client.post("/api/auth/passkeys/login/options").json()
    cred = key.get(opts)
    assert client.post("/api/auth/passkeys/login", json={"credential": cred}).status_code == 200
    _sign_out(client)
    # replaying the same signed response fails - its challenge was consumed
    assert client.post("/api/auth/passkeys/login", json={"credential": cred}).status_code == 400
    # a fresh challenge cookie can't be satisfied with an old response either
    client.post("/api/auth/passkeys/login/options")
    assert client.post("/api/auth/passkeys/login", json={"credential": cred}).status_code == 400
    assert client.get("/api/auth/me").status_code == 401


@pytest.mark.parametrize(
    "tamper",
    [
        {"origin": "https://evil.example"},  # phishing site relaying the challenge
        {"flags": UP},  # no user verification (biometric/PIN)
        {"key": ec.generate_private_key(ec.SECP256R1())},  # wrong private key
    ],
)
def test_bad_assertions_are_rejected(client, tamper):
    enroll(client)
    key = SoftKey()
    assert _add_passkey(client, key).status_code == 200
    _sign_out(client)
    opts = client.post("/api/auth/passkeys/login/options").json()
    r = client.post("/api/auth/passkeys/login", json={"credential": key.get(opts, **tamper)})
    assert r.status_code == 400
    assert client.get("/api/auth/me").status_code == 401


def test_unknown_passkey_and_disabled_account(client):
    enroll(client)
    key = SoftKey()
    assert _add_passkey(client, key).status_code == 200
    _sign_out(client)
    stranger = SoftKey(b"someone-else-123")
    stranger.user_handle = key.user_handle
    opts = client.post("/api/auth/passkeys/login/options").json()
    assert client.post("/api/auth/passkeys/login", json={"credential": stranger.get(opts)}).status_code == 400

    with SessionLocal() as db:
        db.get(User, db.scalar(select(Passkey.user_id))).is_active = False
        db.commit()
    opts = client.post("/api/auth/passkeys/login/options").json()
    assert client.post("/api/auth/passkeys/login", json={"credential": key.get(opts)}).status_code == 403


def test_registration_checks(client):
    # signed-out users can't register
    assert client.post("/api/auth/passkeys/register/options").status_code == 401
    enroll(client)
    key = SoftKey()
    opts = client.post("/api/auth/passkeys/register/options").json()
    bad = client.post("/api/auth/passkeys/register", json={"credential": key.create(opts, origin="https://evil.example")})
    assert bad.status_code == 400
    opts = client.post("/api/auth/passkeys/register/options").json()
    assert client.post("/api/auth/passkeys/register", json={"credential": key.create(opts, flags=UP | AT)}).status_code == 400
    # the same authenticator can't be added twice, and existing ones are excluded up front
    assert _add_passkey(client, key).status_code == 200
    opts = client.post("/api/auth/passkeys/register/options").json()
    assert [c["id"] for c in opts["excludeCredentials"]] == [bytes_to_base64url(key.cred_id)]
    assert client.post("/api/auth/passkeys/register", json={"credential": key.create(opts)}).status_code == 400
    assert client.post("/api/auth/passkeys/register", json={"credential": {}, "name": "<b>"}).status_code == 422


def test_remove_passkey(client):
    enroll(client)
    key = SoftKey()
    pid = _add_passkey(client, key).json()["id"]
    _sign_out(client)
    enroll(client, "other@example.com", "Other")
    assert client.delete(f"/api/auth/passkeys/{pid}").status_code == 404  # not yours
    _sign_out(client)
    opts = client.post("/api/auth/passkeys/login/options").json()
    assert client.post("/api/auth/passkeys/login", json={"credential": key.get(opts)}).status_code == 200
    assert client.delete(f"/api/auth/passkeys/{pid}").json() == {"ok": True}
    assert client.get("/api/auth/passkeys").json() == []
    _sign_out(client)
    opts = client.post("/api/auth/passkeys/login/options").json()
    assert client.post("/api/auth/passkeys/login", json={"credential": key.get(opts)}).status_code == 400
