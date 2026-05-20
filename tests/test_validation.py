def test_negative_amount(client, auth_headers):
    res = client.post('/api/transactions/', headers=auth_headers, json={
        'amount': -50, 'description': 'Test', 'category': 'Food', 'type': 'expense'
    })
    assert res.status_code == 400

def test_invalid_type(client, auth_headers):
    res = client.post('/api/transactions/', headers=auth_headers, json={
        'amount': 10, 'description': 'Test', 'category': 'Food', 'type': 'illegal'
    })
    assert res.status_code == 400

def test_missing_required_fields(client, auth_headers):
    res = client.post('/api/transactions/', headers=auth_headers, json={'amount': 10})
    assert res.status_code == 400

def test_description_too_short(client, auth_headers):
    res = client.post('/api/transactions/', headers=auth_headers, json={
        'amount': 10, 'description': 'ab', 'category': 'Food', 'type': 'expense'
    })
    assert res.status_code == 400

def test_empty_body(client, auth_headers):
    res = client.post('/api/transactions/', headers=auth_headers,
                      content_type='application/json', data='')
    assert res.status_code == 400
