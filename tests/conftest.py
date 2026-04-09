import pytest
import os
import tempfile
from src.database import Database
from src.generator import IdentifierGenerator
from app import app as flask_app


@pytest.fixture
def db():
    fd, test_db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    database = Database(test_db_path)
    
    yield database
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def generator(db):
    return IdentifierGenerator(db)


@pytest.fixture
def client(monkeypatch):
    fd, test_db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    from src.database import Database
    from src.generator import IdentifierGenerator
    
    test_db = Database(test_db_path)
    test_generator = IdentifierGenerator(test_db)
    
    import app
    monkeypatch.setattr(app, 'db', test_db)
    monkeypatch.setattr(app, 'generator', test_generator)
    
    flask_app.config['TESTING'] = True
    
    with flask_app.test_client() as test_client:
        yield test_client
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
