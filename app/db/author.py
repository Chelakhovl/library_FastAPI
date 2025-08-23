from sqlalchemy import Column, BigInteger, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Author(Base):
    """
    ORM model for authors.

    Represents book authors with a one-to-many relationship to books.
    """

    __tablename__ = "authors"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(Text, nullable=False, unique=True, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    books = relationship(
        "Book",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Author(id={self.id}, name='{self.name}')>"
