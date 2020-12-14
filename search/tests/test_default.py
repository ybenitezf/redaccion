import json


def test_default_route(client):
    res = client.get('/')
    res = json.loads(res.data)

    assert 'result' in res
    assert res['result'] == 'success'
