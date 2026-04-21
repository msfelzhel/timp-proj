#include "model.h"
#include "view.h"

class Controller {
private:
    Model model;
    View view;

public:
    QString handleRequest(const QString &request);
};
