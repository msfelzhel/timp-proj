#ifndef MODEL_H
#define MODEL_H

#include <QString>

class Model {
public:
    Model();

    bool auth(const QString &login, const QString &password);
    bool reg(const QString &login, const QString &password, const QString &email);
    QString stat(const QString &login);
    bool check(int task, const QString &variant, const QString &answer);

private:
    void initDB();
    void createTable();
};

#endif
