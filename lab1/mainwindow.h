#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QSlider>
#include <QSpinBox>
#include <QDoubleSpinBox>
#include <QLabel>
#include <QComboBox>
#include <QColorDialog>
#include <QPushButton>
#include <QGroupBox>
#include "colorcontroller.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);

private slots:
    void onRgbChanged();
    void onCmykChanged();
    void onLabChanged();
    void onSettingsChanged();
    void onColorPickerClicked();

private:
    ColorController m_controller;
    bool m_isUpdating{false};

    QWidget *m_colorPreview;
    QLabel *m_warningLabel;

    QComboBox *m_illuminantCombo;
    QComboBox *m_cmykMethodCombo;
    QComboBox *m_gamutStrategyCombo;
    QPushButton *m_pickerButton;

    QSpinBox *m_rSpin;
    QSlider *m_rSlider;
    QSpinBox *m_gSpin;
    QSlider *m_gSlider;
    QSpinBox *m_bSpin;
    QSlider *m_bSlider;

    QDoubleSpinBox *m_cSpin;
    QSlider *m_cSlider;
    QDoubleSpinBox *m_mSpin;
    QSlider *m_mSlider;
    QDoubleSpinBox *m_ySpin;
    QSlider *m_ySlider;
    QDoubleSpinBox *m_kSpin;
    QSlider *m_kSlider;

    QDoubleSpinBox *m_lSpin;
    QSlider *m_lSlider;
    QDoubleSpinBox *m_aSpin;
    QSlider *m_aSlider;
    QDoubleSpinBox *m_bLabSpin;
    QSlider *m_bLabSlider;

    enum class Channel
    {
        Red,
        Green,
        Blue,
        Cyan,
        Magenta,
        Yellow,
        Black,
        Lightness,
        LabA,
        LabB
    };

    QWidget *createSettingsPanel();
    QGroupBox *createRgbGroup();
    QGroupBox *createCmykGroup();
    QGroupBox *createLabGroup();
    void connectControls();
    void setSliderGradient(QSlider *slider, Channel channel);
    RgbColor gradientColor(Channel channel, double position) const;
    void setupUi();
    void updateGradients();
    void updateUi();
};

#endif
