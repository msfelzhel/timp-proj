#ifndef SERVER_H
#define SERVER_H

#include <QTcpServer>
#include <QTcpSocket>
#include "controller.h"

/**
 * @brief TCP сервер для обработки клиентских запросов
 */
class Server : public QTcpServer {
    Q_OBJECT

public:
    /**
     * @brief Запуск сервера
     * @param port порт
     */
    void start(quint16 port);

protected:
    /**
     * @brief Обработка нового подключения
     */
    void incomingConnection(qintptr socketDescriptor) override;

private:
    Controller controller;
};

#endif
