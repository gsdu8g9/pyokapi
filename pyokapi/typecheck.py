def is_user_id(user_id):
    if isinstance(user_id, str) and len(user_id) == 12 and user_id.isdecimal():
        return True

    return False


def is_user_ids_list(user_ids_list):
    if isinstance(user_ids_list, list):
        if all(map(is_user_id, user_ids_list)):
            return True
    elif is_user_id(user_ids_list):
        return True

    return False


def is_methods_list(methods_list):
    pass
