import pytest
from app import create_app
from app.models import db as _db

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret',
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db(app):
    yield _db
    _db.session.rollback()

@pytest.fixture
def auth_headers(client):
    client.post('/api/auth/register', json={
        'email': 'fixture@example.com', 'password': 'pass1234'
    })
    res = client.post('/api/auth/login', json={
        'email': 'fixture@example.com', 'password': 'pass1234'
    })
    token = res.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}
