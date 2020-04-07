from flask import Flask, render_template, url_for, redirect, flash, request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import TextField, SelectField, StringField
import VkActivity as va
import usersSearchInDifferentCriteries as usc
import vk_api
import json
import numpy as np
from datetime import datetime
import time
from vk_api.execute import VkFunction
import configparser
from wtforms.validators import Required
import logging
import comparsion_id as cpid 
from wtforms.fields.html5 import DateField
import Cluster_an as clan
import matplotlib.pyplot as plt
import mpld3
import pandas as pd
from prettytable import PrettyTable


class selectm(FlaskForm):
    module = SelectField("Модуль: ", choices=[
    	("act", "Активность пользователя"),
        ("cluster", "Кластеризация сообщества"),
    	("srav", "Сравнение аккаунтов"),
        ("poisk", "Поиск в сообществе")])

class Compare(FlaskForm):
    """
    Данный класс отвечает за ввод ID пользователей для их сравнения
    """
    ids = StringField('Введите ID пользователей через запятую')

class DateForm(FlaskForm):
    """
    Данный класс отвечает за ввод ID пользователя, ID групп и временного промежутка для получения активности
    """
    user_id = StringField('User_id')
    group_id = StringField('Введите id групп')
    from_ = DateField('Введите дату начала', format = '%Y-%m-%d')
    to_ = DateField('Введите дату конца', format = '%Y-%m-%d')

class Clust(FlaskForm):
    """
    Данный класс отвечает за ввод ID группы для анализа"
    """
    group_id = StringField('ID группы')

class Categ(FlaskForm):
    """
    Данный класс отвечает за ввод ID группы и выбор параметров для поиска по сообществу
    """
    group_id = StringField('ID группы')
    sex = SelectField("Пол: ", choices=[
        ("0", "Не важно"), 
        ("2", "Мужской"), 
        ("1", "Женский")])
    age_from = StringField('Возраст от')
    age_to = StringField('Возраст до')
    name = StringField('Имя')
    country = StringField('Страна')
    city = StringField('Город')

app = Flask(__name__, static_url_path = '/home')
#Bootstrap(app)


app.config['SECRET_KEY'] = 'amaya'

@app.route('/home', methods = ['GET', 'POST'])
def home():
    """
    Функция возвращает шаблон home.html при переходе по адресу /home
    """
    return render_template('home.html')


@app.route('/team',methods = ['GET', 'POST'])
def team():
    """
    Функция возвращает шаблон team.html при переходе по адресу /team
    """
    return render_template('team.html')

@app.route('/module1', methods = ['GET', 'POST'])
def module1():
    """
    Функция возвращает шаблон module1.html при переходе по адресу /module1
    """
    module1 = DateForm()
    if module1.validate_on_submit():
        ##flash '<h1> {} {} {}'.format(form.user_id.data, form.from_.data, form.to_.data)
        flash('Данные получены')
        user_id = module1.user_id.data
        user_id = int(user_id)
        group_id = module1.group_id.data
        group_id = str(group_id)
        from_ = module1.from_.data
        from_ = str(from_)
        to_ = module1.to_.data
        to = str(to_)

        def auth():
            """
            Функция авторизации Вконтакте
            """
            conf = configparser.RawConfigParser()
            conf.read("Authorization_vk.ini")
            login = conf.get('Authorization', 'login')
            password = conf.get('Authorization', 'password')
            vk_session = vk_api.VkApi(login, password)
            try:
                vk_session.auth(token_only=True)
                return vk_session
            except vk_api.AuthError as error_msg:
                print(error_msg)

        vk_session = auth()

        tools = vk_api.VkTools(vk_session)
        vk = vk_session.get_api()
        groups = tools.get_all('groups.get', 100, {'user_id': user_id})
        wall = tools.get_all('wall.get', 100, {'owner_id': user_id})
        if (group_id == ''):
            groups_id = groups['items']
        else:
            groups_id = [int(item) for item in group_id.split(',')]
       # print(groups_id)
        #groups_id = groups['items']
#        groups_id = [76982440]
        print(len(groups_id), groups_id)
        from_=str(str(from_)+' 00:00:00')
        to_=str(str(to_)+' 23:59:59')
        # from_ = "13.12.2019 00:00:00"
        # to_ = "14.12.2019 23:59:59"
        d_start = datetime.strptime(from_, "%Y-%m-%d %H:%M:%S")
        t_start = time.mktime(d_start.timetuple())-3600*3
        d_finish = datetime.strptime(to_, "%Y-%m-%d %H:%M:%S")
        t_finish = time.mktime(d_finish.timetuple())-3600*3

        answer = []
        answer_1 = []
        for i in range(len(groups_id)):
            try:
                wall_ = va.get_wall(vk, groups_id[i], t_start, t_finish)
                print('wall get', i + 1, '/', len(groups_id))
                answer.append(va.get_likes(-groups_id[i], user_id, wall_[0], wall_[1], t_start, t_finish, vk_session))
                print('likes processed')
                answer_1.append(
                    va.get_comments(-groups_id[i], user_id, wall_[0], wall_[1], t_start, t_finish, vk_session))
                print('comments processed')
            except:
                answer.append([])
                answer_1.append(([], []))
                print('failed', i, '/', len(groups_id))
        try:
            wall_self = va.get_wall_from(vk, user_id, t_start, t_finish)
            answer_self = va.get_likes_self(user_id, wall_self[0], wall_self[1], wall_self[2], t_start, t_finish,
                                            vk_session)
            answer_self_1 = va.get_comments_self(user_id, wall_self[0], wall_self[1], t_start, t_finish, vk_session)
        except:
            answer_self = ([], [])
            answer_self_1 = ([], [])

        ## Лайки
        likes = []
        y_likes = []
        for i in range(len(answer)):
            likes += answer[i]
        for i in range(len(answer_1)):
            likes += answer_1[i][0]
        likes += answer_self[0]
        likes += answer_self_1[0]
        for i in range(len(likes)):
            y_likes.append(datetime.fromtimestamp(likes[i]).strftime('%Y-%m-%d'))
            likes[i] = datetime.fromtimestamp(likes[i]).strftime('%Y-%m-%d %H:%M:%S')

        ## Комментарии
        comments = []
        y_comments = []
        for i in range(len(answer_1)):
            comments += answer_1[i][1]
        comments += answer_self[1]
        comments += answer_self_1[1]
        for i in range(len(comments)):
            y_comments.append(datetime.fromtimestamp(comments[i]).strftime('%Y-%m-%d'))
            comments[i] = datetime.fromtimestamp(comments[i]).strftime('%Y-%m-%d %H:%M:%S')
        graph = va.act_graph(y_likes, y_comments, d_start, d_finish)
        
        df = pd.DataFrame({'Тип': ['Лайки','Даты Комментарии'], 'Даты': [likes, comments], 'Количество': [len(likes), len(comments)]})
        return render_template('module1result.html',answer_info = answer_1, tables=[df.to_html(classes='data')], titles=df.columns.values,  id=user_id, likes_answer = likes, comments_answer = comments, graph = graph )

    return render_template('module1.html', module1 =module1)

@app.route('/module2', methods = ['GET', 'POST'])
def module2():
    """
    Функция возвращает шаблон module2.html при переходе по адресу /module2
    """
    module2 = Clust()
    if module2.validate_on_submit():
        group_id = module2.group_id.data
        group_id = str(group_id)
        res = clan.module(group_id)
        return render_template('module2result.html',group_id=group_id, result = res)
    return render_template('module2.html', module2=module2)

@app.route('/module3', methods = ['GET', 'POST'])
def module3():
    """
    Функция возвращает шаблон module3.html при переходе по адресу /module3
    """
    module3 = Compare()
    if module3.validate_on_submit():
        ##flash '<h1> {} {} {}'.format(form.user_id.data, form.from_.data, form.to_.data)
        flash('Данные получены')
        ids = module3.ids.data
        ids = str(ids)

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

        def auth():
            conf = configparser.RawConfigParser()
            conf.read("Authorization_vk.ini")
            login = conf.get('Authorization', 'login')
            password = conf.get('Authorization', 'password')
            vk_session = vk_api.VkApi(login, password)
            try:
                vk_session.auth(token_only=True)
                return vk_session
            except vk_api.AuthError as error_msg:
                print(error_msg)
        vk_session = auth()

        comparsion = cpid.compare_by_id(ids, vk_session)
#        print(ids)
#        print(comparsion)
        return render_template('module3result.html', tables=[comparsion.to_html(classes='data')], titles=comparsion.columns.values, ids = ids, result = comparsion)
    return render_template('module3.html', module3=module3)

@app.route('/module4', methods = ['GET', 'POST'])
def module4():
    """
    Функция возвращает шаблон module4.html при переходе по адресу /module4
    """
    module4 = Categ()
    if module4.validate_on_submit():
        dictionary = {'sex': None, 'age_to': None, 'age_from': None, 'city': None, 'country': None, 5: 25, 'q': None}
#        print(dictionary)
        group_id = module4.group_id.data
        group_id = int(group_id)
        def auth():
            conf = configparser.RawConfigParser()
            conf.read("Authorization_vk.ini")
            login = conf.get('Authorization', 'login')
            password = conf.get('Authorization', 'password')
            vk_session = vk_api.VkApi(login, password)
            try:
                vk_session.auth(token_only=True)
                return vk_session
            except vk_api.AuthError as error_msg:
                print(error_msg)
        vk_session = auth()
        tools = vk_api.VkTools(vk_session)
        vk = vk_session.get_api()
        s = request.form['sex']
        if (s == '0'):
            sex = '0'
        elif (s == '1'):
            sex = '1'
            dictionary['sex'] = sex
        elif (s == '2'):
            sex = '2'
            dictionary['sex'] = sex
        try:
            age_from = module4.age_from.data
            age_from = int(age_from)
            dictionary['age_from'] = age_from
        except: 
            u = 1
        try:
            age_to = module4.age_to.data
            age_to = int(age_to)
            dictionary['age_to'] = age_to
        except: 
            u = 1 
        try:
            name = module4.name.data
            name = str(name)
            dictionary['q'] = name
        except: 
            u = 1

        try:
            country = module4.country.data
            country = str(country)
            dictionary['country'] = None
            countries = vk_session.method("database.getCountries", {"need_all": 1, "count": 1000}) 
            for i in countries['items']:
                if i['title']==country:
                    dictionary['country'] = i['id']
                    break
        except:
            u = 1

        try:
            city = module4.city.data
            city = str(city)
            dictionary['city'] = None
            сities = vk_session.method("database.getCities", {"country_id": dictionary['country'], "q":city}) 
            for j in сities['items']:
                if j['title']==city:
                    dictionary['city'] = j['id']
                    break
           # dictionary['city'] = city
        except: 
            u = 1

        criteries = dictionary
        group_id1=group_id

        offset1 = 1
        usrs3 = []
        while offset1 - 1000 <= vk.groups.getById(group_id = group_id1, fields = 'members_count')[0]['members_count']:
            usrs = vk.users.search(q = criteries['q'], sort = 1,  count = 1000, offset = offset1, group_id = group_id1, sex = criteries['sex'], age_from = criteries['age_from'], age_to = criteries['age_to'], city = criteries['city'], country = criteries['country'])
            #на этом этапе в usrs сохраняются данные первых 1000 найденных подписчиков, далее производим сдвиг offset на 1000 на каждой итерации
            for x in usrs['items']: 
                usrs3.append(x['id'])
            #после каждого прохода вынимаем id найденных пользователей и сохраняем в массив usrs3
            offset1 += 1000
        link_arr = []
        info_arr = []
        short_info  = vk.users.get(user_ids=usrs3)
        for i in range (len(usrs3)):
            link = 'http://vk.com/id'+str(usrs3[i])
            link_arr.append(link)
            try:
                info_arr.append([short_info[i]['first_name'],' ',short_info[i]['last_name']])
            except:
                info_arr.append('None')
        print(dictionary)
        df1 = pd.DataFrame({'Ссылка': link_arr, 'Краткая информация': info_arr})
       # ID_users_list = usc.usersSearchInDifferentCriteries(vk_session, dictionary, group_id)
       # ID_users_list = usc.usersSearchInDifferentCriteries(vk_session, dict
        #return str( str(group_id)+ str(sex)+ str(age_from)+ str(age_to)+ str(name)+ str(country)+ str(city) )
        return render_template('module4result.html',len = len(usrs3),  group_id = group_id1, ids = usrs3, titles=df1.columns.values, tables=[df1.to_html(classes='data')])
    return render_template('module4.html', module4=module4)





if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 8000)
