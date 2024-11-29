import uuid

import pytest_asyncio
from faker import Faker
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.entity import User, Role, UserRole, UserLoginHistory

fake = Faker()


def generate_fake_role():
    return Role(
        id=uuid.uuid4(),
        name=fake.job(),
        description=fake.text(max_nb_chars=100),
        permissions=[fake.word() for _ in range(3)],
        created_at=fake.date_time_this_decade(),
        updated_at=fake.date_time_this_decade(),
    )


def generate_fake_user():
    return User(
        id=uuid.uuid4(),
        login=fake.user_name(),
        password=fake.password(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        is_active=fake.boolean(),
        is_superuser=fake.boolean(),
        created_at=fake.date_time_this_decade(),
        updated_at=fake.date_time_this_decade(),
    )


def generate_fake_user_role(user_id, role_id):
    return UserRole(
        id=uuid.uuid4(),
        user_id=user_id,
        role_id=role_id,
        created_at=fake.date_time_this_decade(),
        updated_at=fake.date_time_this_decade(),
    )


def generate_fake_login_history(user_id):
    return UserLoginHistory(
        id=uuid.uuid4(),
        user_id=user_id,
        login_time=fake.date_time_this_year(),
        user_agent=fake.user_agent(),
        ip_address=fake.ipv4(),
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def data_upload(
    db_session: AsyncSession, num_users: int = 10, num_roles: int = 5
):
    roles = [generate_fake_role() for _ in range(num_roles)]
    users = [generate_fake_user() for _ in range(num_users)]

    db_session.add_all(roles)
    db_session.add_all(users)
    await db_session.commit()

    user_roles = [
        generate_fake_user_role(user.id, fake.random_element(roles).id)
        for user in users
    ]
    db_session.add_all(user_roles)

    login_histories = [generate_fake_login_history(user.id) for user in users]
    db_session.add_all(login_histories)

    await db_session.commit()

    yield None


@pytest_asyncio.fixture(scope="session")
def create_user(db_session: AsyncSession, make_post_request):
    async def inner(login: str, password: str, is_superuser: bool = False):
        await make_post_request(
            "/api/v1/auth/register",
            form_data={"login": login, "password": password},
        )

        if is_superuser:
            await db_session.execute(
                update(User)
                .where(User.login == "superuser")
                .values(**{"is_superuser": True})
            )
            await db_session.commit()

    return inner


@pytest_asyncio.fixture(scope="session")
async def access_token_of_superuser(create_user, make_post_request):
    login = "superuser"
    password = "123456"

    await create_user(login=login, password=password, is_superuser=True)

    response_login = await make_post_request(
        "/api/v1/auth/login",
        form_data={"login": login, "password": "123456"},
    )
    return response_login.body["access_token"]


@pytest_asyncio.fixture(scope="session")
async def access_token_of_user(create_user, make_post_request):
    login = "user"
    password = "123456"

    await create_user(login=login, password=password, is_superuser=False)

    response_login = await make_post_request(
        "/api/v1/auth/login",
        form_data={"login": login, "password": password},
    )
    return response_login.body["access_token"]
