import vk_api
#модуль для выстаскивания подписчиков определенной группы по указанным критериям
def usersSearchInDifferentCriteries(vk_session, criteries, group_id1): 
    vk_session.auth()
    vk = vk_session.get_api()
    tools = vk_api.VkTools(vk_session)
    offset1 = 1
    usrs3 = []
    while offset1 - 1000 <= vk.groups.getById(group_id = group_id1, fields = 'members_count')[0]['members_count']:
            usrs = vk.users.search(q = criteries['q'], sort = 1,  count = 1000, offset = offset1, group_id = group_id1, sex = criteries['sex'], age_from = criteries['age_from'], age_to = criteries['age_to'], city = criteries['city'], country = criteries['country'])
            #на этом этапе в usrs сохраняются данные первых 1000 найденных подписчиков, далее производим сдвиг offset на 1000 на каждой итерации
            for x in usrs['items']: 
                usrs3.append(x['id'])
            #после каждого прохода вынимаем id найденных пользователей и сохраняем в массив usrs3
            offset1 += 1000
    return usrs3


