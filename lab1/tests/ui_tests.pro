TEMPLATE = app
TARGET = ui_tests
QT += widgets testlib
CONFIG += console c++17 testcase
CONFIG -= app_bundle
SOURCES += ui_tests.cpp ../mainwindow.cpp ../colormodel.cpp ../colorcontroller.cpp
HEADERS += ../mainwindow.h ../colormodel.h ../colorcontroller.h
