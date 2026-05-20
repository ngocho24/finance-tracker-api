def test_create_transaction(client, auth_headers):
    res = client.post('/api/transactions/', headers=auth_headers, json={
        'amount': 50.00, 'description': 'Coffee', 'category': 'Food', 'type': 'expense'
    })
    assert res.status_code == 201
    assert res.get_json()['transaction']['amount'] == '50.00'

def test_get_transactions(client, auth_headers):
    client.post('/api/transactions/', headers=auth_headers, json={
        'amount': 100.00, 'description': 'Salary', 'category': 'Work', 'type': 'income'
    })
    res = client.get('/api/transactions/', headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_filter_by_category(client, auth_headers):
    client.post('/api/transactions/', headers=auth_headers, json={
        'amount': 20.00, 'description': 'Bus fare', 'category': 'Transport', 'type': 'expense'
    })
    res = client.get('/api/transactions/?category=Transport', headers=auth_headers)
    assert all(t['category'] == 'Transport' for t in res.get_json())

def test_filter_by_type(client, auth_headers):
    client.post('/api/transactions/', headers=auth_headers, json={
        'amount': 100.00, 'description': 'Salary', 'category': 'Work', 'type': 'income'
    })
    res = client.get('/api/transactions/?type=income', headers=auth_headers)
    assert all(t['type'] == 'income' for t in res.get_json())

def test_summary(client, auth_headers):
    res = client.get('/api/transactions/summary', headers=auth_headers)
    data = res.get_json()
    assert 'total_income' in data
    assert 'total_expense' in data
    assert 'net_balance' in data

def test_user_isolation(client):
    client.post('/api/auth/register', json={'email': 'u1@example.com', 'password': 'pass1234'})
    client.post('/api/auth/register', json={'email': 'u2@example.com', 'password': 'pass1234'})
    r1 = client.post('/api/auth/login', json={'email': 'u1@example.com', 'password': 'pass1234'})
    r2 = client.post('/api/auth/login', json={'email': 'u2@example.com', 'password': 'pass1234'})
    h1 = {'Authorization': f"Bearer {r1.get_json()['access_token']}"}
    h2 = {'Authorization': f"Bearer {r2.get_json()['access_token']}"}
    client.post('/api/transactions/', headers=h1, json={
        'amount': 999.00, 'description': 'Secret', 'category': 'Private', 'type': 'income'
    })
    res = client.get('/api/transactions/', headers=h2)
    assert all(t['description'] != 'Secret' for t in res.get_json())
