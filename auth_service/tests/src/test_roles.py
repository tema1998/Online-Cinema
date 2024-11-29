from http import HTTPStatus
from select import select

import pytest
from sqlalchemy import select

from src import Role, User, UserRole

api_url = "/api/v1/roles"


@pytest.mark.asyncio
class TestRoles:

    async def test_get_roles_by_auth_superuser(
        self, make_get_request, access_token_of_superuser
    ):
        response = await make_get_request(
            f"{api_url}",
            headers={"Authorization": f"Bearer {access_token_of_superuser}"},
        )
        assert response.status == HTTPStatus.OK
        assert len(response.body["roles"]) == 5

    async def test_get_roles_by_auth_user(self, make_get_request, access_token_of_user):
        response = await make_get_request(
            f"{api_url}",
            headers={"Authorization": f"Bearer {access_token_of_user}"},
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert (
            response.body["detail"] == "You must be a superuser to execute this action."
        )

    async def test_get_roles_by_not_auth_user(self, make_get_request):
        response = await make_get_request(
            f"{api_url}",
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert response.body["detail"] == "Not authenticated"

    async def test_create_role_by_auth_superuser(
        self, make_post_request, access_token_of_superuser
    ):
        response = await make_post_request(
            f"{api_url}",
            form_data={
                "name": "name_of_role",
                "description": "description",
                "permissions": ["permission1", "permission2"],
            },
            headers={"Authorization": f"Bearer {access_token_of_superuser}"},
        )
        assert response.status == HTTPStatus.OK
        assert response.body["name"] == "name_of_role"
        assert response.body["description"] == "description"
        assert response.body["permissions"] == ["permission1", "permission2"]

    async def test_create_role_by_auth_user(
        self, make_post_request, access_token_of_user
    ):
        response = await make_post_request(
            f"{api_url}",
            form_data={
                "name": "name_of_role",
                "description": "description",
                "permissions": ["permission1", "permission2"],
            },
            headers={"Authorization": f"Bearer {access_token_of_user}"},
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert (
            response.body["detail"] == "You must be a superuser to execute this action."
        )

    async def test_create_role_by_not_auth_user(self, make_post_request):
        response = await make_post_request(
            f"{api_url}",
            form_data={
                "name": "name_of_role",
                "description": "description",
                "permissions": ["permission1", "permission2"],
            },
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert response.body["detail"] == "Not authenticated"

    async def test_delete_role_by_auth_superuser(
        self, make_delete_request, access_token_of_superuser, db_session
    ):
        role_executed_query = await db_session.execute(select(Role))
        role = role_executed_query.scalars().first()

        response = await make_delete_request(
            f"{api_url}/{role.id}",
            headers={"Authorization": f"Bearer {access_token_of_superuser}"},
        )
        assert response.status == HTTPStatus.OK
        assert response.body["detail"] == "Role successfully deleted."

    async def test_delete_role_with_not_uuid_id(
        self, make_delete_request, access_token_of_superuser, db_session
    ):
        response = await make_delete_request(
            f"{api_url}/not_uuid_id",
            headers={"Authorization": f"Bearer {access_token_of_superuser}"},
        )
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.body["detail"] == "Enter correct UUID."

    async def test_delete_not_existing_role(
        self, make_delete_request, access_token_of_superuser, db_session
    ):
        role_executed_query = await db_session.execute(select(Role))
        role = role_executed_query.scalars().first()

        response = await make_delete_request(
            f"{api_url}/00000000-706d-4a6a-ab9a-bff65ed787c7",
            headers={"Authorization": f"Bearer {access_token_of_superuser}"},
        )
        assert response.status == HTTPStatus.BAD_REQUEST
        assert response.body["detail"] == "Role doesn't exist."

    async def test_delete_role_by_auth_user(
        self, make_delete_request, access_token_of_user, db_session
    ):
        role_executed_query = await db_session.execute(select(Role))
        role = role_executed_query.scalars().first()

        response = await make_delete_request(
            f"{api_url}/{role.id}",
            headers={"Authorization": f"Bearer {access_token_of_user}"},
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert (
            response.body["detail"] == "You must be a superuser to execute this action."
        )

    async def test_delete_role_by_not_auth_user(self, make_delete_request, db_session):
        role_executed_query = await db_session.execute(select(Role))
        role = role_executed_query.scalars().first()

        response = await make_delete_request(
            f"{api_url}/{role.id}",
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert response.body["detail"] == "Not authenticated"

    async def test_update_role_by_auth_superuser(
        self, make_update_request, access_token_of_superuser, db_session
    ):
        role_before_updating_executed_query = await db_session.execute(select(Role))
        role_before_updating = role_before_updating_executed_query.scalars().first()

        response = await make_update_request(
            f"{api_url}/{role_before_updating.id}",
            form_data={
                "name": "new_name",
                "description": "new_description",
                "permissions": ["new_permission"],
            },
            headers={"Authorization": f"Bearer {access_token_of_superuser}"},
        )

        assert response.status == HTTPStatus.OK
        assert response.body["name"] == "new_name"
        assert response.body["description"] == "new_description"
        assert response.body["permissions"] == ["new_permission"]

    async def test_update_role_by_auth_user(
        self, make_update_request, access_token_of_user, db_session
    ):
        role_before_updating_executed_query = await db_session.execute(select(Role))
        role_before_updating = role_before_updating_executed_query.scalars().first()

        response = await make_update_request(
            f"{api_url}/{role_before_updating.id}",
            form_data={
                "name": "new_name",
                "description": "new_description",
                "permissions": ["new_permission"],
            },
            headers={"Authorization": f"Bearer {access_token_of_user}"},
        )

        assert response.status == HTTPStatus.UNAUTHORIZED
        assert (
            response.body["detail"] == "You must be a superuser to execute this action."
        )

    async def test_update_role_by_not_auth_user(self, make_update_request, db_session):
        role_before_updating_executed_query = await db_session.execute(select(Role))
        role_before_updating = role_before_updating_executed_query.scalars().first()

        response = await make_update_request(
            f"{api_url}/{role_before_updating.id}",
            form_data={
                "name": "new_name",
                "description": "new_description",
                "permissions": ["new_permission"],
            },
        )

        assert response.status == HTTPStatus.UNAUTHORIZED
        assert response.body["detail"] == "Not authenticated"

    async def test_assign_role_to_user_by_auth_superuser(
        self, make_post_request, access_token_of_superuser, db_session
    ):
        role_executed_query = await db_session.execute(select(Role))
        role = role_executed_query.scalars().first()

        user_executed_query = await db_session.execute(
            select(User).where(User.login == "superuser")
        )
        user = user_executed_query.scalars().first()

        response = await make_post_request(
            f"{api_url}/{user.id}/assign",
            form_data={"role_name": role.name},
            headers={"Authorization": f"Bearer {access_token_of_superuser}"},
        )
        assert response.status == HTTPStatus.OK
        assert (
            response.body["detail"]
            == f"Role '{role.name}' successfully assigned to user with ID: '{user.id}'."
        )

    async def test_assign_role_to_user_by_auth_user(
        self, make_post_request, access_token_of_user, db_session
    ):
        role_executed_query = await db_session.execute(select(Role))
        role = role_executed_query.scalars().first()

        user_executed_query = await db_session.execute(
            select(User).where(User.login == "superuser")
        )
        user = user_executed_query.scalars().first()

        response = await make_post_request(
            f"{api_url}/{user.id}/assign",
            form_data={"role_name": role.name},
            headers={"Authorization": f"Bearer {access_token_of_user}"},
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert (
            response.body["detail"] == "You must be a superuser to execute this action."
        )

    async def test_assign_role_to_user_by_not_auth_user(
        self, make_post_request, db_session
    ):
        role_executed_query = await db_session.execute(select(Role))
        role = role_executed_query.scalars().first()

        user_executed_query = await db_session.execute(
            select(User).where(User.login == "superuser")
        )
        user = user_executed_query.scalars().first()

        response = await make_post_request(
            f"{api_url}/{user.id}/assign",
            form_data={"role_name": role.name},
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert response.body["detail"] == "Not authenticated"

    async def test_permissions_of_user_by_auth_superuser(
        self, make_get_request, access_token_of_superuser, db_session
    ):
        user_executed_query = await db_session.execute(
            select(User).where(User.login == "superuser")
        )
        user = user_executed_query.scalars().first()

        user_role_executed_query = await db_session.execute(
            select(UserRole).where(UserRole.user_id == user.id)
        )
        user_role = user_role_executed_query.scalars().first()

        role_executed_query = await db_session.execute(
            select(Role).where(Role.id == user_role.role_id)
        )
        role = role_executed_query.scalars().first()

        response = await make_get_request(
            f"{api_url}/{user_role.user_id}/permissions",
            headers={"Authorization": f"Bearer {access_token_of_superuser}"},
        )
        assert response.status == HTTPStatus.OK
        assert response.body["permissions"] == role.permissions

    async def test_permissions_of_user_by_auth_user(
        self, make_get_request, access_token_of_user, db_session
    ):
        user_executed_query = await db_session.execute(
            select(User).where(User.login == "superuser")
        )
        user = user_executed_query.scalars().first()

        user_role_executed_query = await db_session.execute(
            select(UserRole).where(UserRole.user_id == user.id)
        )
        user_role = user_role_executed_query.scalars().first()

        response = await make_get_request(
            f"{api_url}/{user_role.user_id}/permissions",
            headers={"Authorization": f"Bearer {access_token_of_user}"},
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert (
            response.body["detail"] == "You must be a superuser to execute this action."
        )

    async def test_permissions_of_user_by_no_auth_user(
        self, make_get_request, db_session
    ):
        user_executed_query = await db_session.execute(
            select(User).where(User.login == "superuser")
        )
        user = user_executed_query.scalars().first()

        user_role_executed_query = await db_session.execute(
            select(UserRole).where(UserRole.user_id == user.id)
        )
        user_role = user_role_executed_query.scalars().first()

        response = await make_get_request(
            f"{api_url}/{user_role.user_id}/permissions",
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert response.body["detail"] == "Not authenticated"

    async def test_remove_role_from_user_by_auth_superuser(
        self, make_delete_request, access_token_of_superuser, db_session
    ):
        user_executed_query = await db_session.execute(
            select(User).where(User.login == "superuser")
        )
        user = user_executed_query.scalars().first()

        user_role_executed_query = await db_session.execute(
            select(UserRole).where(UserRole.user_id == user.id)
        )
        user_role = user_role_executed_query.scalars().first()

        role_executed_query = await db_session.execute(
            select(Role).where(Role.id == user_role.role_id)
        )
        role = role_executed_query.scalars().first()

        response = await make_delete_request(
            f"{api_url}/{user_role.user_id}/remove",
            form_data={"role_name": role.name},
            headers={"Authorization": f"Bearer {access_token_of_superuser}"},
        )
        assert response.status == HTTPStatus.OK
        assert (
            response.body["detail"]
            == f"Role '{role.name}' successfully removed from user with ID: '{user_role.user_id}'."
        )

    async def test_remove_role_from_user_by_auth_user(
        self, make_delete_request, access_token_of_user, db_session
    ):
        user_role_executed_query = await db_session.execute(select(UserRole))
        user_role = user_role_executed_query.scalars().first()

        role_executed_query = await db_session.execute(
            select(Role).where(Role.id == user_role.role_id)
        )
        role = role_executed_query.scalars().first()

        response = await make_delete_request(
            f"{api_url}/{user_role.user_id}/remove",
            form_data={"role_name": role.name},
            headers={"Authorization": f"Bearer {access_token_of_user}"},
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert (
            response.body["detail"] == "You must be a superuser to execute this action."
        )

    async def test_remove_role_from_user_by_no_auth_user(
        self, make_delete_request, db_session
    ):
        user_role_executed_query = await db_session.execute(select(UserRole))
        user_role = user_role_executed_query.scalars().first()

        role_executed_query = await db_session.execute(
            select(Role).where(Role.id == user_role.role_id)
        )
        role = role_executed_query.scalars().first()

        response = await make_delete_request(
            f"{api_url}/{user_role.user_id}/remove",
            form_data={"role_name": role.name},
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert response.body["detail"] == "Not authenticated"
