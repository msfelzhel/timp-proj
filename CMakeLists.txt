cmake_minimum_required(VERSION 3.16)

project(timp_tsp_server)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Включаем Qt (Core + Network)
find_package(Qt6 REQUIRED COMPONENTS Core Network)
# если у тебя Qt5, замени на:
# find_package(Qt5 REQUIRED COMPONENTS Core Network)

# Исполняемый файл
add_executable(timp_tsp_server
    main.cpp
    server.cpp server.h
    controller.cpp controller.h
    model.cpp model.h
    view.cpp view.h
    sqlite3.c
)

# Говорим что sqlite это C файл
set_source_files_properties(sqlite3.c PROPERTIES LANGUAGE C)

# Линкуем Qt
target_link_libraries(timp_tsp_server PRIVATE
    Qt6::Core
    Qt6::Network
)
# для Qt5:
# target_link_libraries(timp_tsp_server PRIVATE Qt5::Core Qt5::Network)
