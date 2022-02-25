import unittest
from flask import url_for
from flask_testing import TestCase
from app import app

class SettingBase(TestCase):
    def create_app(self):
        return app
        
    def setUp(self):
        self.email = "leolee@iii.org.tw"
        self.password = "azazaz"

    def login(self):
        response = self.client.post(
            url_for('login'),
            follow_redirects=True,
            json={
                "email": self.email,
                "password": self.password
            }
        )
        return response

class CheckUserAndLogin(SettingBase):
    def test_login_successfully(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)

    def test_login_failed(self):
        self.password = '123456'
        response = self.login()
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
