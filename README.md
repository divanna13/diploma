# diploma

parent
    tg_id integer
    tg_username string
    first_name string
    last_name string
    phone string

    @relation:
        has_many children
        has_many children -> accounts
      
children
    first_name string
    last_name string
    parent_id integer
    group_id integer

    @relation
        belongs_to parent
        belongs_to group
        has_one account

group
    price integer
    name string
    price integer
    @relations
        has_many children
        belongs_to garden

garden
    name string
    @relation
        has_many groups

attending #посещаемость
    created_at date
    children_id integer
    group_id integer
    @relation
        belongs_to children
        belongs_to group



Сценарии родителя:

    1. Подключиться к боту
    2. Добавление ребенка "Введите ФИО ребенка"
    

Сценарии администратора:
    0. Необходимо узнать и сохранить id администратора
        добавить его в app.py
    1. Отправить ссылку на бот родителю
    2. При получении уведолмения о получении родителя и инфы о его детях он может: 
        2.1 Добавить ребенка к саду
        2.2 Добавить ребенка к группе
        2.3 Удалить ребенка из группы
        2.4 Переместить ребенка в другую группу
    3.Посмотреть информацию по ребенку, саду, группе, по оплате
    4.Добавить оплату за ребенка/группу за колво занятий
    5.Отправить информацию об оплате родителю за ребенка/группу/колво занятий
    6.Скачать файл csv


Статья https://habr.com/ru/articles/787976/

`docker-compose up` Старт контейнеров

Для запуска только бота не в контейнере: 

    ```shell
    cd ./bot
    # инсталляция библиотек, делается один раз
    pip install -r requirements.txt

    # запуск бота
    python app.py
    ```