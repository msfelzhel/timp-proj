#ifndef VIEW_H
#define VIEW_H

#include <QStringList>

class View {
public:
    QStringList parse(const QString &request);
};

#endif
