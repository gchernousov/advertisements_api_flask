def users_list(users):
    user_list = []
    for user in users:
        user_info = {'id': user.id, 'name': user.username, 'advertisements': len(user.advertisements)}
        user_list.append(user_info)

    return user_list


def advertisements_list(advertisements):
    adv_list = []
    for advertisement in advertisements:
        adv = {'id': advertisement.id, 'title': advertisement.title, 'created': advertisement.created}
        adv_list.append(adv)

    return adv_list