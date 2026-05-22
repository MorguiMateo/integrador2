from passlib.context import CryptContext


# Contexto global de hashing.
# Se recomienda reutilizar una única instancia.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,#12 rounds tarda ~250ms por verificación, es seguro pero no afecta la UX
)


def get_password_hash(password: str) -> str:# Genera un hash bcrypt a partir de una contraseña en texto plano
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )