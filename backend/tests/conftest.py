import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.seed import load_sample_data
TEST_DB_NAME = "doomsday_test"
@pytest.fixture(scope="session")
def session_factory():
    main_url = make_url(settings.database_url)
    admin = create_engine(main_url, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": TEST_DB_NAME}
        )
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin.dispose()
    engine = create_engine(main_url.set(database=TEST_DB_NAME))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    engine.dispose()
@pytest.fixture
def client(session_factory):
    with session_factory() as db:
        load_sample_data(db)
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
