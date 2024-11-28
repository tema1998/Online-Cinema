
def check_user_permission_for_film(user:dict, film: dict) -> bool:
    if film['premium']:
        if user['is_premium']:
            return True
        return False
    return True