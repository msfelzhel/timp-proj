#ifndef EMAIL_SERVICE_H
#define EMAIL_SERVICE_H

#include <QString>

class EmailService {
public:
    static QString generateCode();
    static bool sendCode(const QString &to, const QString &code);
};

#endif // EMAIL_SERVICE_H
