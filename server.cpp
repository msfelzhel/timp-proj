#include "server.h"
#include <QTcpSocket>

    /**
 * @brief Конструктор
 */
    Server::Server(QObject *parent) : QTcpServer(parent) {}

/**
 * @brief Запуск сервера
 */
void Server::start(quint16 port) {
    listen(QHostAddress::Any, port);
}

/**
 * @brief Новое подключение
 */
void Server::incomingConnection(qintptr socketDescriptor) {
    QTcpSocket *socket = new QTcpSocket(this);
    socket->setSocketDescriptor(socketDescriptor);

    connect(socket, &QTcpSocket::readyRead, this, [=]() {
        QByteArray data = socket->readAll();

        if (data.trimmed().isEmpty())
            return;

        QString request = QString::fromUtf8(data).trimmed();

        QString response = controller.handleRequest(request);

        if (!response.isEmpty())
            socket->write((response + "\n").toUtf8());
    });

    connect(socket, &QTcpSocket::disconnected, socket, &QTcpSocket::deleteLater);
}

