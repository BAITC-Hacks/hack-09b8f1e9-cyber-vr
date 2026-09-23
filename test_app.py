import io
import json
import app as server


def test_health(monkeypatch):
    monkeypatch.delenv('ORGLENS_ACCESS_TOKEN', raising=False)
    assert server.app.test_client().get('/api/health').status_code == 200


def test_no_key(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('ORGLENS_ACCESS_TOKEN', raising=False)
    assert server.app.test_client().post('/api/analyze').status_code == 503


def test_requires_consent(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'mock-for-offline-tests')
    monkeypatch.delenv('ORGLENS_ACCESS_TOKEN', raising=False)
    assert server.app.test_client().post('/api/analyze', data={'before_text':'A', 'after_text':'B'}).status_code == 400


def test_analysis_uses_grounded_ids(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'mock-for-offline-tests')
    monkeypatch.delenv('ORGLENS_ACCESS_TOKEN', raising=False)
    def mocked(messages, schema=None):
        return json.dumps({'summary':'Требует проверки', 'structure_changes':[], 'lost_functions':[
            {'title':'Функция контроля', 'explanation':'Проверьте передачу функции', 'before_ids':['B0001','NONEXISTENT'], 'after_ids':['B0001']}],
            'duplicate_functions':[], 'new_functions':[], 'recommendations':[]})
    monkeypatch.setattr(server, 'call_ai', mocked)
    r=server.app.test_client().post('/api/analyze',data={'before_text':'Контроль качества обращений', 'after_text':'Отдел обращений', 'consent':'yes'})
    assert r.status_code == 200
    j=r.get_json(); assert j['lost_functions'][0]['before_ids']==['B0001']
    assert j['lost_functions'][0]['after_ids']==[]
    assert j['evidence']['B0001']['text']=='Контроль качества обращений'


def test_unsupported_upload(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'mock-for-offline-tests')
    monkeypatch.delenv('ORGLENS_ACCESS_TOKEN', raising=False)
    r=server.app.test_client().post('/api/analyze',data={'consent':'yes','before':(io.BytesIO(b'nope'), 'test.exe'),'after_text':'After'})
    assert r.status_code==400


def test_access_gate(monkeypatch):
    monkeypatch.setenv('ORGLENS_ACCESS_TOKEN','secret')
    assert server.app.test_client().get('/api/health').status_code==401
    assert server.app.test_client().get('/api/health',headers={'X-OrgLens-Token':'secret'}).status_code==200


def test_home():
    assert server.app.test_client().get('/').status_code==200
