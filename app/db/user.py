from sqlalchemy import Column, BigInteger, Text, TIMESTAMP, func
from app.db.base import Base


class User(Base):
    """
    ORM model for users.

    Represents an application user with email, hashed password,
    and creation timestamp.
    """

    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(Text, unique=True, nullable=False, index=True)
    hashed_password = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
