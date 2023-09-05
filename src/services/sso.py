from dotenv import load_dotenv
from envs import env
from keycloak import KeycloakOpenID
from singleton_decorator import singleton

load_dotenv()


@singleton
class SSO:
    def __init__(self):
        self.client_id = env("KEYCLOAK_CLIENT_ID", var_type="string", allow_none=False)
        self.client_secret_key = env(
            "KEYCLOAK_CLIENT_SECRET_KEY", var_type="string", allow_none=False
        )
        self.kc_openid = KeycloakOpenID(
            server_url=env("KEYCLOAK_SERVER_URL", var_type="string", allow_none=False),
            client_id=self.client_id,
            realm_name=env("KEYCLOAK_REALM", var_type="string", allow_none=False),
            client_secret_key=self.client_secret_key,
        )
        self.active_token = None

    def get_token(self):
        self.active_token = self.kc_openid.token(
            self.client_id, self.client_secret_key, grant_type=["client_credentials"]
        )
        return self.active_token

    def get_user_id(self):
        token = self.get_token()
        userinfo = self.kc_openid.userinfo(token["access_token"])
        return userinfo["sub"]