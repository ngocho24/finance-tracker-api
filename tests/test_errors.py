def test_404_returns_json(client):
    res = client.get('/api/nonexistent')
    assert res.status_code == 404
    assert res.is_json

def test_401_returns_json(client):
    res = client.get('/api/transactions/')
    assert res.status_code == 401
    assert res.is_json

def test_malformed_json(client, auth_headers):
    res = client.post('/api/transactions/', headers=auth_headers,
                      content_type='application/json', data='{bad json}')
    assert res.status_code == 400
