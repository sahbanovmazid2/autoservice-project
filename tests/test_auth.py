"""Проверки входа, регистрации и прав пользователей."""
import tempfile
import unittest
from pathlib import Path
from core_database import init_database
from auth import login, register_user, hash_password, verify_password
from main import admin_actions, client_actions


class TestAuthorization(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'auth_test.db'
        init_database(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def test_admin_login(self):
        self.assertEqual(login('admin', 'admin123', self.db)['role'], 'admin')

    def test_wrong_password(self):
        self.assertIsNone(login('admin', 'wrongpass', self.db))
        self.assertIsNone(login('unknown', 'admin123', self.db))

    def test_reader_login(self):
        register_user('student12', 'reader123', db_path=self.db)
        self.assertEqual(login('student12', 'reader123', self.db)['role'], 'user')

    def test_password_hashing(self):
        a = hash_password('reader123')
        b = hash_password('reader123')
        self.assertNotEqual(a, b)
        self.assertTrue(verify_password('reader123', a))
        self.assertFalse(verify_password('wrongpass', a))

    def test_role_permissions(self):
        self.assertIn('3', admin_actions())
        self.assertNotIn('3', client_actions())


if __name__ == '__main__':
    unittest.main()
