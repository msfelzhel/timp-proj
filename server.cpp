#include "server.h"

/**
 * @brief Запуск прослушивания порта
 */
void Server::start(quint16 port) {
    listen(QHostAddress::Any, port);
}

/**
 * @brief Обработка входящего соединения
 */
void Server::incomingConnection(qintptr socketDescriptor) {
    QTcpSocket *socket = new QTcpSocket;
    socket->setSocketDescriptor(socketDescriptor);

    connect(socket, &QTcpSocket::readyRead, [=]() {
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
