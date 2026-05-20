def test_register_success(client):
    res = client.post('/api/auth/register', json={
        'email': 'new@example.com', 'password': 'pass1234'
    })
    assert res.status_code == 201
    assert res.get_json()['msg'] == 'User created successfully'

def test_register_duplicate_email(client):
    client.post('/api/auth/register', json={'email': 'dup@example.com', 'password': 'pass1234'})
    res = client.post('/api/auth/register', json={'email': 'dup@example.com', 'password': 'pass1234'})
    assert res.status_code == 400

def test_login_returns_token(client):
    client.post('/api/auth/register', json={'email': 'login@example.com', 'password': 'pass1234'})
    res = client.post('/api/auth/login', json={'email': 'login@example.com', 'password': 'pass1234'})
    assert res.status_code == 200
    assert 'access_token' in res.get_json()

def test_login_wrong_password(client):
    client.post('/api/auth/register', json={'email': 'wp@example.com', 'password': 'pass1234'})
    res = client.post('/api/auth/login', json={'email': 'wp@example.com', 'password': 'wrongpass'})
    assert res.status_code == 401

def test_password_is_hashed(client, db):
    from app.models import User
    client.post('/api/auth/register', json={'email': 'hash@example.com', 'password': 'pass1234'})
    user = User.query.filter_by(email='hash@example.com').first()
    assert user.password != 'pass1234'
    assert user.check_password('pass1234')

def test_protected_route_without_token(client):
    res = client.get('/api/transactions/')
    assert res.status_code == 401
