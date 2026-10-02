"""Passkeys (WebAuthn): add them in the profile, then sign in without a code."""
import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Passkey, User
from ..schemas import me_out
from ..security import passkeys
from ..security.deps import audit, get_current_user
from .auth import _start_session, auth_limit

router = APIRouter(prefix="/api/auth/passkeys", tags=["passkeys"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


class RegisterIn(BaseModel):
    credential: dict[str, Any]
    name: str = Field("Passkey", min_length=1, max_length=60, pattern=r"^[^<>]*$")


class LoginIn(BaseModel):
    credential: dict[str, Any]


@router.get("")
def list_passkeys(user: CurrentUser, db: DB):
    rows = db.scalars(select(Passkey).where(Passkey.user_id == user.id).order_by(Passkey.created_at)).all()
    return [passkeys.public(p) for p in rows]


@router.post("/register/options", dependencies=[Depends(auth_limit())])
def register_options(response: Response, user: CurrentUser, db: DB):
    return json.loads(passkeys.registration_options(db, response, user))


@router.post("/register", dependencies=[Depends(auth_limit())])
def register(body: RegisterIn, request: Request, response: Response, user: CurrentUser, db: DB):
    pk = passkeys.register(db, request, response, user, body.credential, body.name.strip())
    audit(db, request, "passkey_added", user.id, pk.name)
    db.commit()
    return passkeys.public(pk)


@router.delete("/{passkey_id}")
def remove(passkey_id: int, request: Request, user: CurrentUser, db: DB):
    pk = db.get(Passkey, passkey_id)
    if pk is None or pk.user_id != user.id:
        raise HTTPException(404, "Not found")
    db.delete(pk)
    audit(db, request, "passkey_removed", user.id, pk.name)
    db.commit()
    return {"ok": True}


@router.post("/login/options", dependencies=[Depends(auth_limit())])
def login_options(response: Response, db: DB):
    return json.loads(passkeys.login_options(db, response))


@router.post("/login", dependencies=[Depends(auth_limit())])
def login(body: LoginIn, request: Request, response: Response, db: DB):
    try:
        user = passkeys.authenticate(db, request, response, body.credential)
    except HTTPException:
        audit(db, request, "passkey_login_failed")
        db.commit()
        raise
    _start_session(db, request, response, user)
    audit(db, request, "login_passkey", user.id)
    db.commit()
    return {"user": me_out(db, user)}
