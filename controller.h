#ifndef CONTROLLER_H
#define CONTROLLER_H

#include "model.h"
#include "view.h"

class Controller {
public:
    QString handleRequest(const QString &request);

private:
    Model model;
    View view;
};

#endif
