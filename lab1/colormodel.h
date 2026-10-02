#ifndef COLORMODEL_H
#define COLORMODEL_H
#include <array>
enum class Illuminant
{
    D65,
    D50,
    E
};

enum class CmykMethod
{
    UCR,
    GCR
};

enum class GamutStrategy
{
    Clipping,
    Scaling
};

struct RgbColor
{
    double r, g, b;
};

struct CmykColor
{
    double c, m, y, k;
};

struct XyzColor
{
    double x, y, z;
};

struct LabColor
{
    double l, a, b;
};

using Matrix3 = std::array<std::array<double, 3>, 3>;

class ColorModel
{
public:
    ColorModel();
    void setIlluminant(Illuminant value);
    const Matrix3 &forwardMatrix() const
    {
        return forward;
    }
    const Matrix3 &inverseMatrix() const
    {
        return backward;
    }
    XyzColor whitePoint() const
    {
        return white;
    }
    XyzColor rgbToXyz(RgbColor rgb) const;
    RgbColor xyzToRgb(XyzColor xyz) const;
    LabColor xyzToLab(XyzColor xyz) const;
    XyzColor labToXyz(LabColor lab) const;
    LabColor rgbToLab(RgbColor rgb) const;
    RgbColor labToRgb(LabColor lab) const;
    static CmykColor rgbToCmyk(RgbColor rgb, CmykMethod method);
    static RgbColor cmykToRgb(CmykColor cmyk);
    static RgbColor mapGamut(RgbColor rgb, GamutStrategy strategy, bool &changed);

private:
    Matrix3 forward{};

    Matrix3 backward{};

    XyzColor white{};
};

#endif
