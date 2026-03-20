import unittest
import json
from app import app, db

class TestBackend(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_quote(self):
        self.app.post('/api/auth/register', json={
            'phone': '9999999999',
            'name': 'Test User',
            'zone': 'Koramangala, BLR',
            'platform': 'Food'
        })
        res = self.app.post('/api/quote', json={
            'phone': '9999999999',
            'zone': 'Koramangala, BLR',
            'platform': 'Food'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('weekly_premium', data)

    def test_simulate(self):
        self.app.post('/api/auth/register', json={
            'phone': '8888888888',
            'name': 'Sim User',
            'zone': 'Koramangala, BLR',
            'platform': 'Food'
        })
        self.app.post('/api/quote', json={
            'phone': '8888888888',
            'zone': 'Koramangala, BLR',
            'platform': 'Food'
        })
        res = self.app.post('/api/simulate-disruption', json={
            'phone': '8888888888',
            'type': 'rainstorm'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'triggered')

    def test_worker_data(self):
        self.app.post('/api/auth/register', json={
            'phone': '7777777777',
            'name': 'Worker User',
            'zone': 'Koramangala, BLR',
            'platform': 'Food'
        })
        self.app.post('/api/quote', json={
            'phone': '7777777777',
            'zone': 'Koramangala, BLR',
            'platform': 'Food'
        })
        res = self.app.get('/api/worker/data?phone=7777777777')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIsNotNone(data['policy'])
        self.assertEqual(data['policy']['platform'], 'Food')

if __name__ == '__main__':
    unittest.main()
