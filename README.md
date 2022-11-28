### Начало работы

Поднять базу данных с помощью докера:
> docker-compose up -d

Установить зависимости:
> pip install -r requirements.txt

___

### Работа с API

- Проверка работы:

```GET http://127.0.0.1:5000/```

- Ожидаемый ответ:

```{"status": "OK"}```

- Список пользователей:

```GET http://127.0.0.1:5000/user/```

- Информация о пользователе:

```GET http://127.0.0.1:5000/user/<id>```

- Регистрация пользователя: 
1. Имя должно состоять как минимум из 2-х букв, но не больше 32-х
2. Пароль должен быть длиннее 8 знаков и содержать маленькие и большие буквы, числа и прочие символы (@$!%*#?&_)
3. email указывать необязательно

```
{"username": логин, "password": пароль, "email": почта}

POST http://127.0.0.1:5000/user/
```

- Показать все объявления:

```GET http://127.0.0.1:5000/advertisement/```

- Показать информацию об объявлении:

```GET http://127.0.0.1:5000/advertisement/<id>```

Для следующих запросов необходимо передать в заголовках логин и пароль.
- Добавить новое объявление:

```
{"title": заголовок, "description": текст объявления}

POST http://127.0.0.1:5000/advertisement/
```

- Изменить объявление:

```
{"title": заголовок, "description": текст объявления}

PATCH http://127.0.0.1:5000/advertisement/<id>
```

- Удалить объявление:

```DELETE http://127.0.0.1:5000/advertisement/<id>```