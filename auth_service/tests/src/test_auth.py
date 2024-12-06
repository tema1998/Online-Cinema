import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import text

from src.models.entity import User
from src.services.user_service import UserService
from tests.settings import test_settings


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    # Use the db_session fixture to perform a simple query
    result = await db_session.execute(text("SELECT 1"))

    # Fetch the result
    value = result.scalar()

    # Assert that the query returned the expected value
    assert value == 1


@pytest.mark.asyncio
async def test_register_user(db_session: AsyncSession):
    async with AsyncClient(base_url=test_settings.api_url, timeout=30.0) as ac:
        # Define the registration data
        registration_data = {
            "login": "testuser",
            "password": "securepassword",
            "first_name": "FirstName",
            "last_name": "LastName",
        }

        # Send the POST request to the registration endpoint
        response = await ac.post("/api/v1/auth/register", json=registration_data)

        # Assert that the response status code is 201 CREATED
        assert response.status_code == status.HTTP_201_CREATED

        # Assert the response contains the expected user data
        data = response.json()
        assert data["login"] == registration_data["login"]
        assert "password" not in data  # Ensure password is not returned in the response

        # Optionally, check that the user was actually created in the database
        stmt = select(User).filter_by(login=registration_data["login"])
        result = await db_session.execute(stmt)
        user_in_db = result.scalars().first()

        assert user_in_db is not None
        assert user_in_db.login == registration_data["login"]


@pytest.mark.asyncio
async def test_login_user(db_session: AsyncSession, user_service: UserService):
    # First, register a user to test the login
    async with AsyncClient(base_url=test_settings.api_url, timeout=30.0) as ac:
        registration_data = {
            "login": "testuser1",
            "password": "securepassword1",
            "first_name": "FirstName1",
            "last_name": "LastName1",
        }

        # Register the user
        register_response = await ac.post(
            "/api/v1/auth/register", json=registration_data
        )
        assert register_response.status_code == status.HTTP_201_CREATED

        # Now define the login data
        login_data = {
            "login": registration_data["login"],
            "password": registration_data["password"],
        }

        # Send the POST request to the login endpoint
        response = await ac.post("/api/v1/auth/login", json=login_data)

        # Assert that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK

        # Assert the response contains the expected token data
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Verify that the user ID in the token matches the registered user
        user_id_from_token = await user_service.get_user_id_from_token(
            data["access_token"]
        )
        #
        # Check that the user was actually created in the database and the token is correct
        stmt = select(User).filter_by(login=registration_data["login"])
        result = await db_session.execute(stmt)
        user_in_db = result.scalars().first()
        assert user_in_db is not None
        assert str(user_id_from_token) == str(user_in_db.id)


@pytest.mark.asyncio
async def test_refresh_user_token(user_service, db_session: AsyncSession):
    # Step 1: Register a user to test the refresh token functionality
    async with AsyncClient(base_url=test_settings.api_url, timeout=30.0) as ac:
        registration_data = {
            "login": "testuser3",
            "password": "securepassword3",
            "first_name": "FirstName3",
            "last_name": "LastName3",
        }

        # Register the user
        register_response = await ac.post(
            "/api/v1/auth/register", json=registration_data
        )
        assert register_response.status_code == status.HTTP_201_CREATED

        # Step 2: Login to get the initial access and refresh tokens
        login_data = {
            "login": registration_data["login"],
            "password": registration_data["password"],
        }

        login_response = await ac.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        login_response_data = login_response.json()

        # Verify the tokens are present
        assert "access_token" in login_response_data
        assert "refresh_token" in login_response_data

        # Extract the refresh token
        refresh_token = login_response_data["refresh_token"]

        # Step 3: Test the refresh token endpoint
        refresh_request = {"refresh_token": refresh_token}

        refresh_response = await ac.post("/api/v1/auth/refresh", json=refresh_request)
        assert refresh_response.status_code == status.HTTP_200_OK
        refresh_response_data = refresh_response.json()

        # Assert that new access and refresh tokens are returned
        assert "access_token" in refresh_response_data
        assert "refresh_token" in refresh_response_data
        refresh_response_data_acc = refresh_response_data["refresh_token"]
        login_response_data_acc = login_response_data["refresh_token"]
        # Ensure the new access token is different from the old one
        assert refresh_response_data_acc == login_response_data_acc

        # Optionally, verify the user in the database
        stmt = select(User).filter_by(login=registration_data["login"])
        result = await db_session.execute(stmt)
        user_in_db = result.scalars().first()

        assert user_in_db is not None
        #
        # Verify the user_id in the token matches the registered user
        user_id_from_token = await user_service.get_user_id_from_token(
            refresh_response_data["access_token"]
        )
        assert str(user_id_from_token) == str(user_in_db.id)


@pytest.mark.asyncio
async def test_logout_user(user_service, db_session: AsyncSession):
    # Step 1: Register a user to test the logout functionality
    async with AsyncClient(base_url=test_settings.api_url, timeout=30.0) as ac:
        registration_data = {
            "login": "testuser4",
            "password": "securepassword4",
            "first_name": "FirstName4",
            "last_name": "LastName4",
        }

        # Register the user
        register_response = await ac.post(
            "/api/v1/auth/register", json=registration_data
        )
        assert register_response.status_code == status.HTTP_201_CREATED

        # Step 2: Login to get the initial access and refresh tokens
        login_data = {
            "login": registration_data["login"],
            "password": registration_data["password"],
        }

        login_response = await ac.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        login_response_data = login_response.json()

        # Verify the tokens are present
        assert "access_token" in login_response_data
        assert "refresh_token" in login_response_data

        access_token = login_response_data["access_token"]
        refresh_token = login_response_data["refresh_token"]

        # Step 3: Test the logout endpoint
        logout_request = {"refresh_token": refresh_token}

        headers = {"Authorization": f"Bearer {access_token}"}

        logout_response = await ac.post(
            "/api/v1/auth/logout", json=logout_request, headers=headers
        )
        assert logout_response.status_code == status.HTTP_200_OK
        logout_response_data = logout_response.json()

        # Assert that the response confirms the user was logged out
        assert logout_response_data["detail"] == "User successfully logged out."

        # Step 4: Verify the access token has been invalidated
        with pytest.raises(Exception):
            await user_service.get_user_id_from_token(access_token)


@pytest.mark.asyncio
async def test_update_user_credentials(user_service, db_session: AsyncSession):
    # Step 1: Register a user to test the update functionality
    async with AsyncClient(base_url=test_settings.api_url, timeout=30.0) as ac:
        registration_data = {
            "login": "testuser5",
            "password": "securepassword5",
            "first_name": "FirstName5",
            "last_name": "LastName5",
        }

        # Register the user
        register_response = await ac.post(
            "/api/v1/auth/register", json=registration_data
        )
        assert register_response.status_code == status.HTTP_201_CREATED

        # Step 2: Login to get the initial access token
        login_data = {
            "login": registration_data["login"],
            "password": registration_data["password"],
        }

        login_response = await ac.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        login_response_data = login_response.json()

        # Verify the access token is present
        assert "access_token" in login_response_data
        access_token = login_response_data["access_token"]

        # Step 3: Prepare the update request data
        update_data = {"new_login": "updateduser",
                       "new_password": "newsecurepassword"}

        headers = {"Authorization": f"Bearer {access_token}"}

        # Send the PATCH request to update user credentials
        update_response = await ac.patch(
            "/api/v1/auth/update", json=update_data, headers=headers
        )
        assert update_response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_user_login_history(user_service, db_session: AsyncSession):
    # Step 1: Register a user to test the login history functionality
    async with AsyncClient(base_url=test_settings.api_url, timeout=30.0) as ac:
        registration_data = {
            "login": "testuser6",
            "password": "securepassword6",
            "first_name": "FirstName6",
            "last_name": "LastName6",
        }

        # Register the user
        register_response = await ac.post(
            "/api/v1/auth/register", json=registration_data
        )
        assert register_response.status_code == status.HTTP_201_CREATED

        # Step 2: Login to get the access token
        login_data = {
            "login": registration_data["login"],
            "password": registration_data["password"],
        }

        login_response = await ac.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        login_response_data = login_response.json()

        # Verify the access token is present
        assert "access_token" in login_response_data
        access_token = login_response_data["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        # Step 3: Fetch the login history for the user
        login_history_response = await ac.get(
            "/api/v1/auth/login-history", headers=headers
        )
        assert login_history_response.status_code == status.HTTP_200_OK

        # Verify the login history data
        login_history_data = login_history_response.json()

        # Check the structure of the paginated response
        assert "count" in login_history_data
        assert "results" in login_history_data
        assert isinstance(login_history_data["results"], list)

        # Ensure there is at least one entry in the login history
        assert len(login_history_data["results"]) > 0

        # Check the structure of the login history entries
        for entry in login_history_data["results"]:
            assert "login_time" in entry
            assert "user_agent" in entry
            assert "ip_address" in entry
            assert entry["user_agent"] == "python-httpx/0.27.2"
            assert entry["ip_address"] is not None
