import httpx
from fastapi import Depends
from fastapi import HTTPException, status

from src.core.config import settings
from src.db.models import OAuthAccount, User
from src.repositories.oauth import OAuthRepository
from src.repositories.role import RoleRepository
from src.repositories.user import UserRepository
from src.utils.general import make_random_string


class YandexOAuthService:
    """
    Service providing interaction with Yandex OAuth
    """

    oauth_provider_name = "yandex"
    http_client = httpx.AsyncClient()

    def __init__(
            self,
            oauth_repo: OAuthRepository = Depends(OAuthRepository),
            user_repo: UserRepository = Depends(UserRepository),
            role_repo: RoleRepository = Depends(RoleRepository),
    ):
        self.oauth_repo = oauth_repo
        self.user_repo = user_repo
        self.role_repo = role_repo

    async def generate_redirect_url(self, session_state: str) -> str:
        """
        Generates redirect URL for Yandex OAuth
        """
        redirect_url = (f"{settings.yandex_oauth_authorize_url}"
                        f"?response_type=code&client_id={settings.yandex_oauth_client_id}"
                        f"&redirect_uri={settings.yandex_oauth_redirect_uri}"
                        f"&state={session_state}")

        return redirect_url

    async def get_service_user(self, code: str):
        """
        Gets online cinema service user
        """

        token = await self.get_token_from_provider(code)
        user_data_from_provider = await self.get_user_data_from_provider(token)

        oauth_user_id = user_data_from_provider.get("id")
        oauth_user = await self.oauth_repo.get_oauth_user(oauth_user_id, self.oauth_provider_name)

        if oauth_user:
            service_user = await self.user_repo.get_user_by_id(oauth_user.user_id)

            return service_user

        new_user = User(
            login=user_data_from_provider.get("login"),
            email=make_random_string(),
            password=make_random_string(),
            first_name=user_data_from_provider.get("first_name"),
            last_name=user_data_from_provider.get("last_name"),
        )
        role_id = await self.role_repo.role_id_by_name(settings.default_user_role)
        new_user.role_id = role_id
        service_user = await self.user_repo.create_user(new_user)

        new_oauth_account = OAuthAccount(
            user_id=service_user.id,
            oauth_user_id=user_data_from_provider.get("id"),
            oauth_provider_name=self.oauth_provider_name,
        )
        await self.oauth_repo.create_oauth_account(new_oauth_account)

        return service_user

    async def get_token_from_provider(self, code: str) -> str | None:
        """
        Gets user token from Yandex OAuth
        """
        response_w_token = await self.http_client.post(
            url=settings.yandex_oauth_token_url,
            data={
                "code": code,
                "grant_type": "authorization_code",
                "client_id": settings.yandex_oauth_client_id,
                "client_secret": settings.yandex_oauth_client_secret,
            },
        )

        if response_w_token.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Something gone wrong with Yandex OAuth."
            )

        response_w_token = response_w_token.json()
        token = response_w_token.get("access_token")

        return token

    async def get_user_data_from_provider(self, token: str) -> dict | None:
        """
        Gets user data from Yandex OAuth
        """
        headers = {
            "Authorization": f"OAuth {token}"
        }
        response_w_user_data = await self.http_client.get(
            url=settings.yandex_oauth_info_url,
            headers=headers,
        )

        if response_w_user_data.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Something gone wrong with Yandex OAuth."
            )

        response_w_user_data = response_w_user_data.json()

        return response_w_user_data
