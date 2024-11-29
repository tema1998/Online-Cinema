def check_user_permission_for_film(user: dict, film: dict) -> bool:
    """
    Function check is film premium or not. Then check is user has a premium status.
    :param user:
    :param film:
    :return: bool
    """
    if film["premium"]:
        if user["is_premium"]:
            return True
        return False
    return True
