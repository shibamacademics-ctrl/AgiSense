import os
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text, create_engine, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

_raw_db_url = os.getenv("DATABASE_URL")
if _raw_db_url:
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif _raw_db_url.startswith("postgresql://") and not _raw_db_url.startswith("postgresql+"):
        _raw_db_url = _raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)

DATABASE_URL = _raw_db_url or "sqlite:///./agisense.db"


class Base(DeclarativeBase):
    pass


class FarmerQuery(Base):
    __tablename__ = "farmer_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farmer_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    query_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    request_payload: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    response_payload: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


_is_sqlite = DATABASE_URL.startswith("sqlite")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=not _is_sqlite,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    """Create application tables when DATABASE_URL is configured.

    For production, run the SQL migration in migrations/001_create_farmer_queries.sql
    through your migration system instead of relying only on startup creation.
    """
    if engine is not None:
        Base.metadata.create_all(bind=engine)


# Auto-create tables for local SQLite so querying never throws "no such table"
if _is_sqlite and engine is not None:
    try:
        init_db()
    except Exception:
        pass


def save_query(
    *,
    query_type: str,
    request_payload: dict[str, Any],
    response_payload: dict[str, Any],
    farmer_id: Optional[str] = None,
) -> Optional[FarmerQuery]:
    if SessionLocal is None:
        return None
    with SessionLocal.begin() as session:
        record = FarmerQuery(
            farmer_id=farmer_id,
            query_type=query_type,
            request_payload=request_payload,
            response_payload=response_payload,
        )
        session.add(record)
        session.flush()
        return record


def list_queries(*, farmer_id: Optional[str] = None, limit: int = 50) -> list[FarmerQuery]:
    if SessionLocal is None:
        return []
    with SessionLocal() as session:
        statement = select(FarmerQuery)
        if farmer_id:
            statement = statement.where(FarmerQuery.farmer_id == farmer_id)
        statement = statement.order_by(FarmerQuery.created_at.desc()).limit(limit)
        return list(session.scalars(statement))


def get_user_by_email(email: str) -> Optional[User]:
    if SessionLocal is None:
        return None
    with SessionLocal() as session:
        return session.scalar(select(User).where(User.email == email.lower()))


def get_user_by_id(user_id: int) -> Optional[User]:
    if SessionLocal is None:
        return None
    with SessionLocal() as session:
        return session.get(User, user_id)


def create_user(*, name: str, email: str, password_hash: str) -> Optional[User]:
    if SessionLocal is None:
        return None
    with SessionLocal.begin() as session:
        user = User(name=name.strip(), email=email.lower(), password_hash=password_hash)
        session.add(user)
        session.flush()
        return user
