# TCP Server (Qt + C++)

Консольный TCP сервер для обработки пользовательских запросов.

## Описание

Сервер принимает TCP соединения и обрабатывает команды:

- авторизация
- регистрация
- получение статистики
- проверка решения задачи

Используется архитектура MVC и база данных SQLite.

## Технологии

- C++
- Qt (QTcpServer)
- SQLite3
- CMake
- Docker

## Архитектура

Проект реализован по паттерну MVC:

- Server  
  Отвечает за сеть. Принимает подключения и передает данные в Controller.

- Controller  
  Обрабатывает команды и вызывает методы Model.

- Model  
  Работает с SQLite. Хранит пользователей.

- View  
  Парсит входящие строки.

## Протокол

Все сообщения текстовые. Разделитель: &

### Авторизация

Запрос:
`auth&login&password`

Ответ:
```
auth+&login
```
```
auth-
```

### Регистрация

Запрос: ```reg&login&password&email```

Ответ:

```reg+&login```

```reg-```

### Статистика

Запрос: ```stat&login```

Ответ: ```stat&3$6&21```
### Проверка задачи

Запрос:

```check&task&variant&answer```

Ответ:
```
check+
```
```
check-
```

## Сборка и запуск

### Через Qt Creator

1. Открыть проект
2. Собрать (Ctrl+B)
3. Запустить (Ctrl+R)

Сервер слушает порт:
`1234`

---

### Через CMake

```mkdir build
cd build
cmake ..
make
./timp_tsp_server
```

---

### Тестирование

Подключение:

`telnet localhost 1234`

Пример:

```reg&user&1234&mail@test.com```

```auth&user&1234```

---

## База данных

Используется SQLite.

Файл создается автоматически:
users.db

Структура таблицы:

```SQL
CREATE TABLE users (
    login TEXT PRIMARY KEY,
    password TEXT,
    email TEXT
);
```

---

## Docker

### Сборка

```
docker build -t tcp_server .
```
### Запуск
```
docker run -p 1234:1234 tcp_server
```
### Подключение
```
telnet localhost 1234
```
---

## Документация

Документация генерируется через Doxygen.
```
doxygen
```
Результат:
```
docs/html/index.html
```
---

## Пример работы
```
reg&test&1234&test@mail.com
auth&test&1234
check&1&a&42
```
---


