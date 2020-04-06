#coding utf-8
import vk_api
import json
import logging
import pandas as pd

def info():
    s = ("Метод данного модуля выводит информацию о пользователях, чьи id были поданы на вход.") + '\n' + (
        "Информация содержит поля:")
    s += ("'first_name' - имя пользователя; 'last_name': фамилия;") + '\n'
    s += ("'is_closed': закрыт ли профиль; 'can_access_closed': может ли текущий пользователь видеть профиль;") + '\n'
    s += ("'sex': пол(1-женщина, 2-мужчина,0 - не указан); 'bdate': дата рождения(день.месяц.год);") + '\n'
    s += ("'country': id и имя страны;'city': id и название города;") + '\n'
    s += (
        "'relation' - статус отношений человека; 'universities' - список университетов(имя, факультет, дата окончания).")
    res = json.dumps(s)
    return res


def compare_by_id(ids, vk_session):
    vk = vk_session.get_api()
#    logging.basicConfig(filename="sample.log", level=logging.INFO)
    try:
        info = vk.users.get(user_ids=ids, fields='sex,bdate,country,city,education,universities,relation')
    except vk_api.ApiError as error_msg:
       logging.error(error_msg)
    result = {}
    women, men, single, in_relations = 0, 0, 0, 0
    cities = {}
    countries = {}
    universities = {}
    private_profiles = 0
    for i in range(len(info)):
        if (info[i]['sex'] == 2):
            men += 1
        elif (info[i]['sex'] == 1):
            women += 1
        if (info[i]['is_closed'] == True):
            private_profiles += 1
            continue
        try:
            if (info[i]['relation'] == 2 or info[i]['relation'] == 3 or info[i]['relation'] == 4 or info[i]['relation'] == 8):
                in_relations += 1
            elif (info[i]['relation'] == 1 or info[i]['relation'] == 6):
                single += 1
        except:
            continue
        # для городов создаем словарь [{город1}:{количество пользователей из такого города},{город2}:.....]
        c = info[i]['city']['title']
        if (cities.get(c) == None):
            cities[c] = 1
        else:
            cities[c] += 1
        # аналогично для стран [{страна1}:{количество пользователей из такой страны},.....]
        c = info[i]['country']['title']
        if (countries.get(c) == None):
            countries[c] = 1
        else:
            countries[c] += 1
        # аналогично для университетов, но их у каждого пользователя может быть несколько
        for x in info[i]['universities']:
            c = x['name']
            if (universities.get(c) == None):
                universities[c] = 1
            else:
                universities[c] += 1
    l_cities = list(cities.items())
    l_countries = list(countries.items())
    l_universities = list(universities.items())
    l_countries.sort(key=lambda i: i[1], reverse=True)
    l_cities.sort(key=lambda i: i[1], reverse=True)
    l_universities.sort(key=lambda i: i[1], reverse=True)
    # считаем, сколько профилей закрыто
    count_closed = 0
    for i in info:
        if (i['is_closed'] == True):
            count_closed += 1
    if (men / (len(info)) == 1):
        result['Совпадение по полу'] = "Все переданные пользователи - мужчины"
    elif (women / (len(info)) == 1):
        result['Совпадение по полу'] = "Все переданные пользователи - женщины"
    else:
        result['Совпадение по полу'] = "Мужчин среди переданных пользователей - " + str(
            men / (len(info)) * 100) + '%, женщин - ' + str(women / (len(info)) * 100) + '%'

    if (count_closed == len(info)):
        result[""] = "Все переданные профили являются закрытыми, другая информация недоступна"
        res = json.dumps(result)
        return res
    if (single == 0 and in_relations == 0):
        result['Совпадение по семейному положению'] = "Информации о семейном положении нет"
    elif (single / (len(info)) == 1):
        result['Совпадение по семейному положению'] = "Все переданные пользователи не находятся в отношениях"
    elif (in_relations / (len(info)) == 1):
        result['Совпадение по семейному положению'] = "Все переданные пользователи находятся в отношениях"
    else:
        result['Совпадение по семейному положению'] = "Среди переданных пользователей в отношениях - " + str(in_relations / (len(info)) * 100) +'%, свободных- ' + str(single / (len(info)) * 100) + '%'
    if (l_countries[0][1] == len(info)):
        result['Совпадение по стране'] = "Все пользователи из страны " + str(l_countries[0][0])
    elif (len(l_countries) == 1):
        result['Совпадение по стране'] = "Все пользователи из страны " + str(l_countries[0][0]) + " (кроме профилей, у которых нет информации о стране)"
    else:
        result['Совпадение по стране'] = "В стране " + str(l_countries[0][0]) + " живет " + str(l_countries[0][1] / len(info) * 100) + " % заданных пользователей, а в стране "+str(l_countries[1][0]) + " живет " + str(l_countries[1][1] / len(info) * 100) + '%'
    if (l_cities[0][1] == len(info)):
        result['Совпадение по городу'] = "Все пользователи из города " + str(l_cities[0][0])
    elif (len(l_cities) == 1):
        result['Совпадение по городу'] = "Все пользователи из города " + str(
            l_cities[0][0]) + " (кроме профилей, у которых нет информации и городе)"
    else:
        result['Совпадение по городу'] = "В городе " + str(l_cities[0][0]) + " живет " + str(l_cities[0][1] / len(info) * 100)+" % заданных пользователей, а в городе " + str(l_cities[1][0]) + " живет " + str(l_countries[1][1] / len(info) * 100) + '%'
    if (l_universities[0][1] == len(info)):
        result['Совпадение по университетам'] = "Все пользователи из университета " + str(l_universities[0][0])
    elif (len(l_universities) == 1):
        result['Совпадение по университетам'] = "Все пользователи из университета " + str(
            l_universities[0][0]) + " (кроме тех, у кого нет информации об университете)"
    else:
        result['Совпадение по университетам'] = "В университете " + str(l_universities[0][0]) + " учится или учились " + str(l_universities[0][1] / len(info) * 100) + " % заданных пользователей, а в университете " + str(l_universities[1][0]) + " учится или учились " + str(l_universities[1][1] / len(info) * 100) + '%'
    #res = json.dumps(result)
    res =pd.DataFrame(result.items(), columns=['Name', 'DateValue'])

    return res

