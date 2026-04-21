#ifndef SERVER_H
#define SERVER_H

#include <QTcpServer>
#include "controller.h"

    class Server : public QTcpServer {
    Q_OBJECT

public:
    explicit Server(QObject *parent = nullptr);

    void start(quint16 port);

protected:
    void incomingConnection(qintptr socketDescriptor) override;

private:
    Controller controller; // ВАЖНО
};

#endif

