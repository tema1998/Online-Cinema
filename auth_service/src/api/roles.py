from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Body, status
from fastapi.responses import JSONResponse

from src.schemas.entity import (
    RoleInDB,
    RoleCreate,
    RolesInDB,
    UpdateRoleRequest,
    UserPermissions,
    AssignDeleteUserRoleRequest,
)
from src.services.role_service import RoleService, get_role_service
from src.utils.role_permissions import only_for_superuser

router = APIRouter()

"""
1.	(DONE) Создание роли:
    •	POST /api/v1/roles
    •	Создание новой роли в системе.
2.	(DONE) Удаление роли:
    •	DELETE /api/v1/roles/{role_id}
    •	Удаление существующей роли.
3.	(DONE) Изменение роли:
    •	PUT /api/v1/roles/{role_id}
    •	Изменение параметров роли.
4.	(DONE) Просмотр всех ролей:
    •	GET /api/v1/roles
    •	Получение списка всех ролей.
5.	(DONE) Назначить пользователю роль:
    •	POST /api/v1/roles/{user_id}/assign
    •	Назначение роли пользователю.
6.	(DONE) Отобрать у пользователя роль:
    •	DELETE /api/v1/roles/{user_id}/remove
    •	Удаление роли у пользователя.
7.	(DONE) Метод для проверки наличия прав у пользователя:
    •	GET /api/v1/roles/{user_id}/permissions
    •	Проверка наличия у пользователя конкретных прав.
"""


@router.post("/", response_model=RoleInDB, summary="Create a role.")
async def create_role(
    role_data: RoleCreate = Body(..., description="Role creation data"),
    role_service: RoleService = Depends(get_role_service),
    check_permission: str = Depends(only_for_superuser),
) -> RoleInDB:
    # Register the user and get the created user's data
    role = await role_service.create_role(role_data.dict())

    # Convert the saved role data to the response model
    return RoleInDB(**role.to_dict())


@router.get("/", response_model=RolesInDB, summary="Get list of roles.")
async def get_roles(
    role_service: RoleService = Depends(get_role_service),
    check_permission: str = Depends(only_for_superuser),
) -> RolesInDB:
    # Register the user and get the created user's data
    roles = await role_service.get_roles()
    return roles


@router.delete("/{role_id}", status_code=HTTPStatus.OK, summary="Delete the role.")
async def delete_role(
    role_id,
    role_service: RoleService = Depends(get_role_service),
    check_permission: str = Depends(only_for_superuser),
):
    await role_service.delete_role(role_id)

    return JSONResponse(
        status_code=HTTPStatus.OK, content={
            "detail": f"Role successfully deleted."}
    )


@router.put("/{role_id}", summary="Update the role.", response_model=RoleInDB)
async def update_role(
    role_id: UUID,
    new_role_data: UpdateRoleRequest = Body(...,
                                            description="New data of role."),
    role_service: RoleService = Depends(get_role_service),
    check_permission: str = Depends(only_for_superuser),
):
    updated_role = await role_service.update_role(role_id, new_role_data)

    return updated_role


@router.post(
    "/{user_id}/assign",
    status_code=status.HTTP_200_OK,
    summary="Assign the role to user.",
)
async def assign_role_to_user(
    user_id: UUID,
    role_data: AssignDeleteUserRoleRequest = Body(
        ..., description="Name of the role."),
    role_service: RoleService = Depends(get_role_service),
    check_permission: str = Depends(only_for_superuser),
):
    await role_service.assign_role_to_user(user_id, role_data.role_name)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "detail": f"Role '{role_data.role_name}' successfully assigned to user with ID: '{user_id}'."
        },
    )


@router.delete(
    "/{user_id}/remove",
    status_code=status.HTTP_200_OK,
    summary="Remove the role from a user.",
)
async def remove_role_from_user(
    user_id: UUID,
    role_data: AssignDeleteUserRoleRequest = Body(
        ..., description="Name of the role."),
    role_service: RoleService = Depends(get_role_service),
    check_permission: str = Depends(only_for_superuser),
):
    await role_service.remove_role_from_user(user_id, role_data.role_name)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "detail": f"Role '{role_data.role_name}' successfully removed from user with ID: '{user_id}'."
        },
    )


@router.get(
    "/{user_id}/permissions",
    status_code=status.HTTP_200_OK,
    summary="Check permissions of user.",
    response_model=UserPermissions,
)
async def check_user_permissions(
    user_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    check_permission: str = Depends(only_for_superuser),
):
    user_permissions = await role_service.check_user_permissions(user_id)

    return user_permissions
