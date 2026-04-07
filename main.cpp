#include <QCoreApplication>
#include "server.h"

/**
 * @brief Точка входа в приложение
 */
int main(int argc, char *argv[]) {
    QCoreApplication a(argc, argv);

    Server server;
    server.start(1234);

    return a.exec();
}
