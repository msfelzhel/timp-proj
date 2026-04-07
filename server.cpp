#include "server.h"

void Server::start(quint16 port) {
    listen(QHostAddress::Any, port);
}

void Server::incomingConnection(qintptr socketDescriptor) {
    QTcpSocket *socket = new QTcpSocket;
    socket->setSocketDescriptor(socketDescriptor);

    connect(socket, &QTcpSocket::readyRead, [=]() {
        QByteArray data = socket->readAll();

        // игнор пустых данных
        if (data.trimmed().isEmpty())
            return;

        QString request = QString::fromUtf8(data).trimmed();

        QString response = controller.handleRequest(request);

        // если есть ответ, отправляем
        if (!response.isEmpty()) {
            socket->write((response + "\n").toUtf8());
        }
    });

    connect(socket, &QTcpSocket::disconnected, socket, &QTcpSocket::deleteLater);
}
