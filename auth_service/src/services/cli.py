import asyncio
from getpass import getpass

import typer
from passlib.context import CryptContext
from werkzeug.security import generate_password_hash

from src.models.entity import User
from src.services.user_service import get_user_service

app = typer.Typer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.command("create-superuser")
def create_superuser():
    """
    Step-by-step creation of a superuser.
    """
    asyncio.run(create_superuser_async())


async def create_superuser_async():
    user_service = get_user_service()

    first_name = typer.prompt("Enter the first name")
    last_name = typer.prompt("Enter the last name")
    login = typer.prompt("Enter the login")

    while True:
        password = getpass("Enter the password: ")
        confirm_password = getpass("Confirm the password: ")
        if password == confirm_password:
            break
        else:
            typer.echo("Passwords do not match. Please try again.")

    hashed_password = generate_password_hash(password)

    existing_user = await user_service.db.fetch_by_query_first(User, "login", login)
    if existing_user:
        typer.echo(f"User with login '{login}' already exists.")
        return

    user = User(
        login=login,
        password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        is_superuser=True,
    )

    await user_service.db.insert(user)
    typer.echo(f"Superuser '{login}' created successfully.")


if __name__ == "__main__":
    app()
