#include "../colorcontroller.h"
#include <cmath>
#include <algorithm>
#include <iostream>
#include <stdexcept>
int checks = 0;
void near(double actual, double expected, double tolerance = 1e-7)
{
    ++checks;
    if (!std::isfinite(actual) || std::abs(actual - expected) > tolerance)
    {
        throw std::runtime_error("Check " + std::to_string(checks) + ": Expected " +
                                 std::to_string(expected) + ", got " + std::to_string(actual));
    }
}

void same(RgbColor a, RgbColor b)
{
    near(a.r, b.r, 1e-6);
    near(a.g, b.g, 1e-6);
    near(a.b, b.b, 1e-6);
}

void testEasyRgb()
{
    ColorModel model;
    LabColor red = model.rgbToLab({255, 0, 0});

    near(red.l, 53.241, 0.002);
    near(red.a, 80.092, 0.002);
    near(red.b, 67.203, 0.002);
    CmykColor ink = ColorModel::rgbToCmyk({255, 0, 0}, CmykMethod::GCR);
    near(ink.c, 0);
    near(ink.m, 1);
    near(ink.y, 1);
    near(ink.k, 0);
    LabColor grayLab = model.rgbToLab({128, 128, 128});
    near(grayLab.l, 53.585, 0.002);
    near(grayLab.a, 0, 0.002);
    near(grayLab.b, 0, 0.002);
}

void testRoundTrips()
{
    ColorModel model;
    Matrix3 d65 = model.forwardMatrix();
    for (Illuminant light : {Illuminant::D65, Illuminant::D50, Illuminant::E})
    {
        model.setIlluminant(light);
        LabColor white = model.rgbToLab({255, 255, 255});
        near(white.l, 100);
        near(white.a, 0);
        near(white.b, 0);
        LabColor black = model.rgbToLab({0, 0, 0});
        near(black.l, 0);
        near(black.a, 0);
        near(black.b, 0);
        if (light != Illuminant::D65)
        {
            near(model.forwardMatrix() == d65, 0);
        }
        const Matrix3 &a = model.forwardMatrix();
        const Matrix3 &b = model.inverseMatrix();
        for (int i = 0; i < 3; ++i)
        {
            for (int j = 0; j < 3; ++j)
            {
                double sum = 0;
                for (int k = 0; k < 3; ++k)
                {
                    sum += a[i][k] * b[k][j];
                }
                double expected = 0;
                if (i == j)
                {
                    expected = 1;
                }
                near(sum, expected);
            }
        }
        for (int r = 0; r <= 255; r += 51)
        {
            for (int g = 0; g <= 255; g += 51)
            {
                for (int b = 0; b <= 255; b += 51)
                {
                    RgbColor rgb{double(r), double(g), double(b)};

                    LabColor lab = model.rgbToLab(rgb);
                    RgbColor restoredRgb = model.labToRgb(lab);
                    same(restoredRgb, rgb);
                    for (CmykMethod method : {CmykMethod::UCR, CmykMethod::GCR})
                    {
                        CmykColor c = ColorModel::rgbToCmyk(rgb, method);
                        for (double v : {c.c, c.m, c.y, c.k})
                        {
                            near(v, std::clamp(v, 0.0, 1.0));
                        }
                        same(ColorModel::cmykToRgb(c), rgb);
                    }
                }
            }
        }
    }
}

void testCmykAndGamut()
{
    CmykColor ucr = ColorModel::rgbToCmyk({128, 128, 128}, CmykMethod::UCR);
    CmykColor gcr = ColorModel::rgbToCmyk({128, 128, 128}, CmykMethod::GCR);
    near(ucr.k, 0);
    near(gcr.k, 1 - 128.0 / 255);
    ucr = ColorModel::rgbToCmyk({51, 51, 51}, CmykMethod::UCR);
    near(ucr.k, 0.48);
    bool changed = false;
    same(ColorModel::mapGamut({-10, 100, 270}, GamutStrategy::Clipping, changed), {0, 100, 255});
    near(changed, 1);
    same(ColorModel::mapGamut({-10, 100, 270}, GamutStrategy::Scaling, changed),
         {0, 110.0 * 255 / 280, 255});
}

void testController()
{
    ColorController controller;
    controller.setFromCmyk(.2, .3, .4, .1);
    near(controller.getCmyk().k, .1);
    controller.setFromLab(50, 120, 120);
    near(controller.isOutOfGamut(), 1);
    RgbColor clipped = controller.getRgb();
    controller.setSettings(Illuminant::D65, CmykMethod::GCR, GamutStrategy::Scaling);
    near(controller.getLab().a, 120);
    near(controller.isOutOfGamut(), 1);
    RgbColor scaled = controller.getRgb();
    double difference = std::abs(clipped.r - scaled.r);
    difference += std::abs(clipped.g - scaled.g);
    difference += std::abs(clipped.b - scaled.b);
    near(difference > 1, true);
}

int main()
{
    try
    {
        testEasyRgb();
        testRoundTrips();
        testCmykAndGamut();
        testController();
        std::cout << "PASS: " << checks << " checks\n";
    }
    catch (const std::exception &error)
    {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 1;
    }
}
