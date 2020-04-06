#!/usr/bin/env python
# coding: utf-8

# In[1]:
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.dates
import mpld3
import vk_api
from vk_api.execute import VkFunction
import pandas as pd

# In[2]:


# Функция предназначена для получение информации со стены группы
# Функция с использованием vk execute
# В качестве параметров принимает: g - id паблика, s - время начала рассматриваемого интервала, f - конец интервала
# Возвращает массивы: id постов и их даты
get_wall = VkFunction(args=('g', 's', 'f'), code='''  
    var posts = API.wall.get({"owner_id": -%(g)s, "count": 100});
    var posts_id = posts.items@.id;
    var posts_date = posts.items@.date;
    var count = posts.count;
    var offset = 100; 
    while (offset < 2500 && offset < count && posts_date[posts_date.length - 1] > %(s)s) 
    {
        var posts = API.wall.get({"owner_id": -%(g)s, "count": 100, "offset": offset}); 
        posts_id = posts_id + posts.items@.id;
        posts_date = posts_date + posts.items@.date;
        offset = offset + 100;
    };
    return [posts_id, posts_date, offset, count];
''')

# In[3]:


# Функция предназначена для получение информации со стены пользователя
# Функция с использованием vk execute
# В качестве параметров принимает: u - id пользователя, s - время начала рассматриваемого интервала, f - конец интервала
# Возвращает массивы: id постов и их даты, а также id автора поста
get_wall_from = VkFunction(args=('u', 's', 'f'), code='''  
    var posts = API.wall.get({"owner_id": %(u)s, "count": 100});
    var posts_id = posts.items@.id;
    var posts_date = posts.items@.date;
    var posts_from = posts.items@.from_id;
    var count = posts.count;
    var offset = 100; 
    while (offset < 2500 && offset < count && posts_date[posts_date.length - 1] > %(s)s) 
    {
        var posts = API.wall.get({"owner_id": %(u)s, "count": 100, "offset": offset}); 
        posts_id = posts_id + posts.items@.id;
        posts_date = posts_date + posts.items@.date;
        posts_from = posts_from + posts.items@.from_id;
        offset = offset + 100;
    };
    return [posts_id, posts_date, posts_from, offset, count];
''')


# Функция предназначена для получение информации о лайках пользователя на странице группы
# Функция с использованием VkTools
# В качестве параметров принимает: id группы, id пользователя, массивы с id постов, массив дат постов,
#                                  начало интервала, конец интервала и сессия вк
# Возвращает массив дат лайков
def get_likes(id, user_id, posts_id, posts_date, start, finish, vk_session):
    tools = vk_api.VkTools(vk_session)
    like_date = []

    lg = len(posts_id)
    print('we go', lg)
    for i in range(lg):
        if (posts_date[i] < start):
            try:
                if (posts_date[i + 1] < start):
                    return like_date
            except:
                pass

        if ((posts_date[i] < finish) and (posts_date[i] > start)):
            try:
                likes = tools.get_all('likes.getList', 1000, {'type': 'post', 'owner_id': id, 'item_id': posts_id[i]})
                print('Количество лайков у поста', len(likes['items']))
                if user_id in likes['items']:
                    like_date.append(posts_date[i])
            except:
                pass

    return like_date


# Функция предназначена для получение информации о лайках пользователя на странице группы
# Функция с использованием VkTools
# В качестве параметров принимает: id группы, id пользователя, массивы с id постов, массив дат постов, массив авторов постов
#                                  начало интервала, конец интервала и сессия вк
# Возвращает массив дат лайков
def get_likes_self(user_id, posts_id, posts_date, posts_from, start, finish, vk_session):
    tools = vk_api.VkTools(vk_session)
    like_date = []
    post_date = []

    lg = len(posts_id)

    for i in range(lg):
        if (posts_date[i] < start):
            try:
                if (posts_date[i + 1] < start):
                    return like_date, post_date
            except:
                pass

        if (posts_date[i] < finish):
            if (posts_from[i] == user_id):
                post_date.append(posts_date[i])
            try:
                likes = tools.get_all('likes.getList', 1000, {'type': 'post', 'owner_id': user_id, 'item_id': posts_id[i]})
                if user_id in likes['items']:
                    like_date.append(posts_date[i])
            except:
                pass

    return like_date, post_date


def get_comments(id, user_id, posts_id, posts_date, start, finish, vk_session):
    tools = vk_api.VkTools(vk_session)
    like_date = []
    com_date = []

    lg = len(posts_id)
    for i in range(lg):
#        print(start, posts_date[i], posts_date[i+1], finish)
        if (posts_date[i] < start):
            try:
                if (posts_date[i + 1] < start):
                    return like_date, com_date
            except:
                pass
        if ((posts_date[i] < finish) and (posts_date[i] > start)):
            try:
                com = tools.get_all('wall.getComments', 100, {'owner_id': id, 'post_id': posts_id[i]})
                lg_1 = len(com['items'])
                print('Количество комментариев под постом', lg_1)
            except:
                com = []
                lg_1 = 0

            for k in range(lg_1):
                try:
                    if (int(user_id) == int(com['items'][k]['from_id'])):
                        com_date.append(com['items'][k]['date'])
                       # print(user_id, ' ',int(com['items'][k]['from_id']),' ', com['items'][k]['date'], com_date) 
                except:
                    pass
                try:
                    likes = tools.get_all('likes.getList', 1000,
                                          {'type': 'comment', 'owner_id': id, 'item_id': com['items'][k]['id']})
                    #print(len(likes['items']
                    if user_id in likes['items']:
                        like_date.append(com['items'][k]['date'])
                except:
                    pass

    return like_date, com_date


def get_comments_self(user_id, posts_id, posts_date, start, finish, vk_session):
    tools = vk_api.VkTools(vk_session)
    like_date = []
    com_date = []

    lg = len(posts_id)

    for i in range(lg):
        if (posts_date[i] < start):
            try:
                if (posts_date[i + 1] < start):
                    return like_date, com_date
            except:
                pass

        if (posts_date[i] < finish):
            try:
                com = tools.get_all('wall.getComments', 100, {'owner_id': user_id, 'post_id': posts_id[i]})
                lg_1 = len(com['items'])
            except:
                com = []
                lg_1 = 0
            for k in range(lg_1):
                try:
                    if (user_id == com['items'][k]['from_id']):
                        com_date.append(com['items'][k]['date'])
                except:
                    pass
                try:
                    likes = tools.get_all('likes.getList', 1000, {'type': 'comment', 'owner_id': user_id, 'item_id': com['items'][k]['id']})
                    if user_id in likes['items']:
                        like_date.append(com['items'][i]['date'])
                except:
                    pass

    return like_date, com_date


def act_graph(likes, comments, start_date, end_date):
    y = Counter(likes)
    y_ = Counter(comments) 
    z = []
    z_ = []
    X = pd.date_range(min(start_date, end_date), max(start_date, end_date)).strftime('%Y-%m-%d').tolist()
    for j in range (len(X)):
        try:
            z.append(y[X[j]])
            z_.append(y_[X[j]])
        except:
            z.append(0)
            z_.append(0)
    fig, ax = plt.subplots()
    ax.plot(X, z, label ='Лайки')
    ax.plot(X, z_, label = 'Комментарии')
    plt.xlabel('Date', fontsize=15, color='blue')
    plt.ylabel('Count', fontsize=15, color='blue')
    graph = mpld3.fig_to_html(fig)
    return graph
