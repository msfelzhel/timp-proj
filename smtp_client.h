#ifndef SMTP_CLIENT_H
#define SMTP_CLIENT_H

#include <QString>

class SmtpClient {
public:
    static bool sendEmail(const QString& to,
                          const QString& subject,
                          const QString& body);
};

#endif
