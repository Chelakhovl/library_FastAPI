from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def create_user(session: AsyncSession, email: str, hashed_password: str):
    """
    Create a new user in the database.
    """
    q = text(
        """
        INSERT INTO users(email, hashed_password)
        VALUES(:e, :p)
        RETURNING id, email, created_at
        """
    )
    result = await session.execute(q, {"e": email, "p": hashed_password})
    await session.commit()
    return result.first()


async def get_user_by_email(session: AsyncSession, email: str):
    """
    Fetch a user by email.
    """
    q = text(
        """
        SELECT id, email, hashed_password, created_at
        FROM users
        WHERE email = :e
        """
    )
    result = await session.execute(q, {"e": email})
    return result.first()
