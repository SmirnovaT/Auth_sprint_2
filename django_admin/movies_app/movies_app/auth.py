import http
import json
import logging

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {'user_login': username, 'password': password}
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        try:
            user, created = User.objects.get_or_create(login=username, )
            user.email = data.get('email')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            logging.debug("Role: ", data.get('role')['name'])
            user.is_admin = data.get('role')['name'] == "admin"
            if not user.is_admin:
                return None
            user.is_staff = data.get('role')['name'] == "admin"
            if data.get('is_active'):
                user.is_active = data.get('is_active')
            else:
                user.is_active = True
            user.save()
        except Exception as e:
            logging.error(f"Exception: {e}")
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None