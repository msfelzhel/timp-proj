#ifndef CONTROLLER_H
#define CONTROLLER_H

#include "model.h"
#include "view.h"

/**
 * @brief Класс обработки логики запросов
 */
class Controller {
public:
    /**
     * @brief Обработка запроса клиента
     * @param request строка запроса
     * @return ответ сервера
     */
    QString handleRequest(const QString &request);

private:
    Model model;
    View view;
};

#endif
