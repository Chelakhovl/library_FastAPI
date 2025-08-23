from sqlalchemy import Column, BigInteger, Text, Integer, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Book(Base):
    __tablename__ = "books"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    genre = Column(Text, nullable=False)
    published_year = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    author_id = Column(BigInteger, ForeignKey("public.authors.id", ondelete="RESTRICT"), nullable=False)

    # зв’язок із автором
    author = relationship("Author", back_populates="books")

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}')>"
