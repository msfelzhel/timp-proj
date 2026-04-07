FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Установка зависимостей
RUN apt update && apt install -y \
    build-essential \
    cmake \
    qt6-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая папка
WORKDIR /app

# Копируем проект
COPY . .

# Сборка
RUN rm -rf build && mkdir build && cd build && cmake .. && make

# Открываем порт
EXPOSE 1234

# Запуск сервера
CMD ["./build/timp_tsp_server"]