from sqlmodel import Field, SQLModel

class FormaPago(SQLModel, table=True):
    __tablename__ = "formas_pago"

    codigo: str = Field(primary_key=True, max_length=20)   
    descripcion: str = Field(max_length=80, nullable=False)
    habilitado: bool = Field(default=True, nullable=False)
