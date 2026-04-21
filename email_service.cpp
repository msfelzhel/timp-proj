
#include "email_service.h"

#include <QSslSocket>
#include <QDebug>
#include <QRandomGenerator>

    static QString b64(const QString &s) {
    return s.toUtf8().toBase64();
}

QString EmailService::generateCode() {
    int code = QRandomGenerator::global()->bounded(100000, 999999);
    return QString::number(code);
}

bool EmailService::sendCode(const QString &to, const QString &code) {

    QSslSocket socket;

    socket.connectToHostEncrypted("smtp.yandex.ru", 465);

    if (!socket.waitForEncrypted(5000)) {
        qDebug() << "SSL NOT ESTABLISHED";
        return false;
    }

    qDebug() << "SSL OK";

    auto read = [&]() {
        if (socket.waitForReadyRead(5000))
            qDebug() << socket.readAll();
    };

    auto send = [&](const QString &cmd) {
        socket.write(cmd.toUtf8());
        socket.waitForBytesWritten();
    };

    read();

    send("EHLO localhost\r\n");
    read();

    send("AUTH LOGIN\r\n");
    read();

    send(b64("felixzhelvis1") + "\r\n");
    read();

    send(b64("fuckrkn1") + "\r\n");
    read();

    send("MAIL FROM:<felixzhelvis1@yandex.ru>\r\n");
    read();

    send("RCPT TO:<" + to + ">\r\n");
    read();

    send("DATA\r\n");
    read();

    QString body =
        "From: Felix <felixzhelvis1@yandex.ru>\r\n"
        "To: " + to + "\r\n"
               "Subject: Password Reset Code\r\n"
               "MIME-Version: 1.0\r\n"
               "Content-Type: text/plain; charset=UTF-8\r\n"
               "\r\n"
               "Your reset code: " + code + "\r\n"
                 "\r\n"
                 ".\r\n";

    send(body);
    read();

    send("QUIT\r\n");

    socket.disconnectFromHost();
    return true;
}

