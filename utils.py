import secrets
import hashlib
import base64
import requests

from config.settings import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI, GITHUB_TOKEN_URL, GITHUB_USER_URL


def generate_code_challenge():
    secret_token = secrets.token_urlsafe(64)
    encoded_secret = base64.urlsafe_b64encode(
        hashlib.sha256(secret_token.encode()).digest()
        ).decode().rstrip("=")
    return secret_token, encoded_secret

def exchange_code_for_token(code, code_verifier):
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "code_verifier": code_verifier,
    }

    headers = {"Accept": "application/json"}

    response = requests.post(GITHUB_TOKEN_URL, data=data, headers=headers)
    response.raise_for_status()
    return response.json()


def get_github_user(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    response = requests.get(GITHUB_USER_URL, headers=headers)
    response.raise_for_status()
    return response.json()