
#ifndef MODEL_H
#define MODEL_H

#include <QString>
#include <QStringList>
#include <sqlite3.h>

    class Model {
public:
    Model();

    // база
    void initDB();
    void createTable();

    // основная логика
    bool reg(const QString &login, const QString &password, const QString &email);
    bool auth(const QString &login, const QString &password);

    QString stat(const QString &login);
    bool check(int task, const QString &variant, const QString &answer);

    QString calc(double a, double b, double c);

    // ===== reset password =====
    bool emailExists(const QString &email);
    bool updatePasswordByEmail(const QString &email, const QString &newPassword);

};

#endif

