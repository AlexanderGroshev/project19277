# coding utf-8
import pandas as pd
import requests
import numpy as np
from datetime import datetime, date, time
import matplotlib.pyplot as plt
import json
from pandas import DataFrame
from sklearn.cluster import KMeans
import mpld3

def info():
    """Здесь расписывается что делает модуль
    """
    s = ("Метод данного модуля выводит информацию о подписчиках сообщества, домен которого был подан на вход.") + '\n'
    s += ("На выходе получается гистограмма распределения подписчиков и кластеризация по возрасту и населенному пункту")
    res = json.dumps(s)
    return res


def take_1000_members(domain):
    token = "5343fbfa5343fbfa5343fbfa75532dfc8d553435343fbfa0d5cf54c0d863d963693d525"
    version = 5.92
    # domain = 'pet_shop_vologda'
    fields = 'bdate,city,country,home_town,last_seen,occupation,relation,sex,education'
    count = 1000
    offset = 0
    all_members = []

    response = requests.get('https://api.vk.com/method/groups.getMembers',
                                params={
                                    'offset': offset,
                                    'count': count,
                                    'access_token': token,
                                    'group_id': domain,
                                    'v': version,
                                    'fields': fields
                                })
    num_items = response.json()['response']['count']
    while (offset < 100000 or num_items > offset):            
        data = response.json()['response']['items']
        offset += count
        all_members.extend(data)
    return all_members


def get_age(birthday_str):
    try:
        birthdate = datetime.strptime(birthday_str, '%d.%m.%Y').date()
        today = date.today()
        age = today.year - birthdate.year
        if today.month < birthdate.month:
            age -= 1
        elif today.month == birthdate.month and today.day < birthdate.day:
            age -= 1
    except ValueError:
        age = '-'
    return age


def module(domain):
    all_memberss = take_1000_members(domain)

    l = len(all_memberss)

    columns = [['id'], ['first_name'], ['last_name'], ['is_closed'], ['can_access_closed'], ['sex'], ['bdate'],
               ['relation'], ['home_town']]

    for col in columns:
        for i in range(0, l):
            try:
                col.append(all_memberss[i][col[0]])
            except KeyError:
                col.append('-')

    columns_dop = [['city', 'id'], ['city', 'title'],
                   ['country', 'id'], ['country', 'title'],
                   ['last_seen', 'time'], ['last_seen', 'platform'],
                   ['occupation', 'type']]

    for col in columns_dop:
        for i in range(0, l):
            try:
                col.append(all_memberss[i][col[0]][col[1]])
            except KeyError:
                col.append('-')

    for col in columns_dop:
        col[0] = col[0] + '_' + col[1]
        del col[1]

    columns.extend(columns_dop)
    data_arr = np.array(columns)
    data_arr = data_arr.transpose()

    df = pd.DataFrame(data_arr[1:], columns=data_arr[0])

    df['age'] = [get_age(str(item)) for item in df['bdate']]

    df1 = df[(df['age'] != '-') & (df['city_id'] != '-')]
    df1 = df1.reset_index(drop=True)
    df1 = df1.sort_values(by='city_title')
    df1 = df1.reset_index(drop=True)
    k = 0
    df1['city_id'][0] = k
    for i in range(1, len(df1)):
        df1['city_id'][i] = k
        if df1['city_title'][i - 1] != df1['city_title'][i]:
            k += 1
    age_w = df['age'][(df.sex == '1') & (df.age != '-')].reset_index(drop=True)
    age_m = df['age'][(df.sex == '2') & (df.age != '-')].reset_index(drop=True)
    bins_w = np.bincount(age_w.values.tolist())
    bins_m = np.bincount(age_m.values.tolist())
    if len(bins_w) > len(bins_m):
        for i in range(len(bins_m), len(bins_w)):
            bins_m = np.append(bins_m, 0)
    else:
        for i in range(len(bins_w), len(bins_m)):
            bins_w = np.append(bins_w, 0)

    fig, ax = plt.subplots()
    x = np.arange(0, len(bins_w))
    ax.bar(x, bins_w.tolist(), color='pink')
    ax.bar(x, bins_m.tolist(), bottom=bins_w.tolist(), color='lightblue')
    fig.set_figwidth(12)  # ширина и
    fig.set_figheight(6)  # высота "Figure"
    ax.legend(['women', 'men'], fontsize=14)
    plt.xlabel('Age', fontsize=14)
    dst_hist = mpld3.fig_to_html(fig)
    plt.savefig('dst_hist.png')
    plt.close()

    Data = {'x': df1['age'],
            'y': df1['city_id']}

    df_1 = DataFrame(Data, columns=['x', 'y'])
    df_1 = df_1.reset_index(drop=True)

    kmeans = KMeans(n_clusters=10).fit(df_1)
    centroids = kmeans.cluster_centers_
    plt.scatter(df_1['x'], df_1['y'], c=kmeans.labels_.astype(float), s=50, alpha=0.5)
    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', s=50)
    plt.xlabel('Age', fontsize=14)
    plt.ylabel('City id', fontsize=14)
    plt.savefig('kmeans.png')
    plt.close()
    return dst_hist
