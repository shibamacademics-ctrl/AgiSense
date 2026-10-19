import os
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

_configured_database_url = os.getenv("DATABASE_URL")
DATABASE_URL = (
    _configured_database_url
    if _configured_database_url and _configured_database_url.startswith(("postgresql://", "postgresql+psycopg://"))
    else None
)


class Base(DeclarativeBase):
    pass


class FarmerQuery(Base):
    __tablename__ = "farmer_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farmer_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    query_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    request_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    response_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False) if engine else None


def init_db() -> None:
    """Create application tables when DATABASE_URL is configured.

    For production, run the SQL migration in migrations/001_create_farmer_queries.sql
    through your migration system instead of relying only on startup creation.
    """
    if engine is not None:
        Base.metadata.create_all(bind=engine)


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
