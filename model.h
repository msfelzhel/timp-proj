#ifndef MODEL_H
#define MODEL_H

#include <QString>

/**
 * @brief Класс работы с базой данных SQLite
 */
class Model {
public:
    /**
     * @brief Конструктор
     */
    Model();

    bool auth(const QString &login, const QString &password);
    bool reg(const QString &login, const QString &password, const QString &email);
    QString stat(const QString &login);
    QString calc(double a, double b, double c);
    bool check(int task, const QString &variant, const QString &answer);

private:
    void initDB();
    void createTable();
};

#endif
