from sqlmodel import SQLModel


class Token(SQLModel):
    """
    Response de autenticación exitosa.

    Devuelto por el endpoint /auth/token
    al completar el login con credenciales válidas.
    """

    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    """
    Payload decodificado del JWT.

    Utilizado internamente en get_current_user
    para identificar al usuario y sus roles.

    Campos:
        sub:    Email del usuario (subject del JWT).
        roles:  Lista de códigos de rol asignados.
    """

    sub: str
    roles: list[str]


class RefreshRequest(SQLModel):
    """
    Body para el endpoint de renovación de tokens.

    El cliente envía el refresh token para
    obtener un nuevo access token sin re-autenticarse.
    """

    refresh_token: str