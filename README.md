# project19277
19277 Статистический анализ аккаунтов в социальных сетях

Задача данного проект - развернуть сервер и запустить сайт, который предоставляет доступ к модулям для получения данных из социальной сети Вконтакте.
Первый шаг создание виртуальной машины на https://cloud.google.com/. Далее представлены сведения об экземпляре ВМ.
![](https://sun9-16.userapi.com/RijYDciK47iYez_HrX6fqnkvz3oL6qtR70P0xg/VXKmZ0TNn6M.jpg)
Затем необходимо подключиться с аккаунта администратора (далее будет использоваться имя пользователя: admin) через SSH. 
Вы окажетесь в директории /home/admin.
На сервере должен быть установлен python3 (а также pip3). Установка с помощью команды apt.
Далее должны быть установлены необходимые python модули с помощью команды pip3:
* flask
* flask_wtf
* wtforms
* wtforms.validators
* wtforms.fields.html5
* vk_api
* json
* numpy 
* datetime
* time
* vk_api.execute
* configparser
* logging
* matplotlib.pyplot 
* mpld3
* pandas
* prettytable
