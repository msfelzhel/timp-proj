#include "smtp_client.h"
#include <QSslSocket>
#include <QDebug>

static void sendCmd(QSslSocket& socket, const QString& cmd) {
    socket.write(cmd.toUtf8() + "\r\n");
    socket.waitForBytesWritten();
    socket.waitForReadyRead();
    qDebug() << socket.readAll();
}

bool SmtpClient::sendEmail(const QString& to,
                           const QString& subject,
                           const QString& body)
{
    QSslSocket socket;

    socket.connectToHostEncrypted("smtp.yandex.ru", 465);
    if (!socket.waitForConnected()) {
        qDebug() << "SMTP connect error";
        return false;
    }

    socket.waitForReadyRead();
    qDebug() << socket.readAll();

    sendCmd(socket, "EHLO localhost");
    sendCmd(socket, "AUTH LOGIN");

    // ЛОГИН (почта)
    sendCmd(socket, QByteArray("felixzhelvis1").toBase64());

    // ПАРОЛЬ ПРИЛОЖЕНИЯ
    sendCmd(socket, QByteArray("fuckrkn1").toBase64());

    sendCmd(socket, "MAIL FROM:<felixzhelvis1@yandex.ru>");
    sendCmd(socket, "RCPT TO:<" + to + ">");
    sendCmd(socket, "DATA");

    QString data =
        "Subject: " + subject + "\r\n"
                                "From: felixzhelvis1@yandex.ru\r\n"
                                "To: " + to + "\r\n"
               "Content-Type: text/plain; charset=UTF-8\r\n\r\n"
        + body + "\r\n.";

    sendCmd(socket, data);

    sendCmd(socket, "QUIT");

    socket.disconnectFromHost();
    return true;
}
