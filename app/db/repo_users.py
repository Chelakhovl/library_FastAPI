from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def create_user(session: AsyncSession, email: str, hashed_password: str):
    """
    Create a new user in the database.

    Args:
        session (AsyncSession): Active database session.
        email (str): User email.
        hashed_password (str): Securely hashed user password.

    Returns:
        Row: Inserted user record (id, email, created_at).
    """
    q = text(
        """
        INSERT INTO users(email, hashed_password)
        VALUES(:e, :p)
        RETURNING id, email, created_at
    """
    )
    return (await session.execute(q, {"e": email, "p": hashed_password})).first()


async def get_user_by_email(session: AsyncSession, email: str):
    """
    Fetch a user by email.

    Args:
        session (AsyncSession): Active database session.
        email (str): Email to look up.

    Returns:
        Row | None: User record if found, otherwise None.
    """
    q = text(
        """
        SELECT id, email, hashed_password, created_at
        FROM users
        WHERE email = :e
    """
    )
    return (await session.execute(q, {"e": email})).first()
