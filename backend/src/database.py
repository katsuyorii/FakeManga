from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .config import settings


async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True, # Убрать при деплое!
)

async_session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
)

class BaseModel(DeclarativeBase):
    ''' Basic SQLAlchemy model with ID primary key field '''
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)