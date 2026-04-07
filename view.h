#ifndef VIEW_H
#define VIEW_H

#include <QStringList>

/**
 * @brief Класс парсинга входящих данных
 */
class View {
public:
    /**
     * @brief Разбор строки запроса
     * @param request строка
     * @return список параметров
     */
    QStringList parse(const QString &request);
};

#endif
