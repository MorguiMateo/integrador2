from datetime import datetime, timezone

from sqlmodel import Session, select

from app.modules.refresh_token.model import RefreshToken


class RefreshTokenRepository:
    """
    Repository para RefreshToken.

    No extiende BaseRepository porque RefreshToken
    no tiene deleted_at y no aplica soft-delete.
    """

    def __init__(self, session: Session):
        self.session = session

    def save(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        """
        Persiste un RefreshToken (create o update).

        Args:
            refresh_token (RefreshToken):
                Instancia a persistir.

        Returns:
            RefreshToken:
                Instancia actualizada tras flush.
        """

        self.session.add(refresh_token)
        self.session.flush()
        self.session.refresh(refresh_token)

        return refresh_token

    def get_by_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        """
        Busca un RefreshToken activo por su hash SHA-256.

        Solo devuelve tokens vigentes:
        - No revocados (revoked_at IS NULL)
        - No expirados (expires_at > ahora)

        Args:
            token_hash (str):
                Hash SHA-256 del token raw.

        Returns:
            RefreshToken | None
        """

        now = datetime.now(timezone.utc)

        statement = (
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .where(RefreshToken.revoked_at.is_(None))
            .where(RefreshToken.expires_at > now)
        )

        return self.session.exec(statement).first()

    def revoke(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        """
        Marca un RefreshToken como revocado seteando revoked_at = now().

        Args:
            refresh_token (RefreshToken):
                Instancia a revocar.

        Returns:
            RefreshToken:
                Instancia actualizada (sin commit).
        """

        refresh_token.revoked_at = datetime.now(timezone.utc)

        self.session.add(refresh_token)
        self.session.flush()

        return refresh_token