from sqlalchemy.orm import Session

from app.core.security import AuthUser
from app.models import User
from app.services.member import request_account_deletion


def test_account_deletion_request_is_idempotent_and_preserves_user(db: Session) -> None:
    user = User(
        id=1,
        username="member",
        password_hash="not-a-plaintext-password",
        role="member",
    )
    db.add(user)
    db.commit()
    auth_user = AuthUser(
        id=user.id,
        username=user.username,
        role=user.role,
        level_code=None,
        phone=None,
    )

    first = request_account_deletion(db, auth_user)
    second = request_account_deletion(db, auth_user)

    assert first.deletion_status == "PENDING"
    assert first.deletion_requested_at is not None
    assert second.deletion_requested_at == first.deletion_requested_at
    assert db.get(User, user.id) is not None
