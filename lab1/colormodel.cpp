#include "colormodel.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace
{
using Vector3 = std::array<double, 3>;
Vector3 multiply(const Matrix3 &m, Vector3 v)
{
    Vector3 result{};

    for (int row = 0; row < 3; ++row)
    {
        for (int col = 0; col < 3; ++col)
        {
            result[row] += m[row][col] * v[col];
        }
    }
    return result;
}

Matrix3 multiply(const Matrix3 &a, const Matrix3 &b)
{
    Matrix3 result{};

    for (int row = 0; row < 3; ++row)
    {
        for (int col = 0; col < 3; ++col)
        {
            for (int k = 0; k < 3; ++k)
            {
                result[row][col] += a[row][k] * b[k][col];
            }
        }
    }
    return result;
}

Matrix3 inverse(Matrix3 a)
{
    Matrix3 result{{{1, 0, 0}, {0, 1, 0}, {0, 0, 1}}};

    for (int col = 0; col < 3; ++col)
    {
        int pivot = col;
        for (int row = col + 1; row < 3; ++row)
        {
            if (std::abs(a[row][col]) > std::abs(a[pivot][col]))
            {
                pivot = row;
            }
        }
        if (std::abs(a[pivot][col]) < 1e-12)
        {
            throw std::runtime_error("Singular matrix");
        }
        std::swap(a[col], a[pivot]);
        std::swap(result[col], result[pivot]);
        double divisor = a[col][col];
        for (int j = 0; j < 3; ++j)
        {
            a[col][j] /= divisor;
            result[col][j] /= divisor;
        }
        for (int row = 0; row < 3; ++row)
        {
            if (row != col)
            {
                double factor = a[row][col];
                for (int j = 0; j < 3; ++j)
                {
                    a[row][j] -= factor * a[col][j];
                    result[row][j] -= factor * result[col][j];
                }
            }
        }
    }
    return result;
}

double removeGamma(double v)
{
    v /= 255.0;
    if (v <= 0.04045)
    {
        return v / 12.92;
    }
    return std::pow((v + 0.055) / 1.055, 2.4);
}

double applyGamma(double v)
{
    if (v <= 0.0031308)
    {
        return 255.0 * 12.92 * v;
    }
    return 255.0 * (1.055 * std::pow(v, 1.0 / 2.4) - 0.055);
}

constexpr double delta = 6.0 / 29.0;
double labFunction(double t)
{
    if (t > delta * delta * delta)
    {
        return std::cbrt(t);
    }
    return t / (3 * delta * delta) + 4.0 / 29.0;
}

double inverseLabFunction(double t)
{
    if (t > delta)
    {
        return t * t * t;
    }
    return 3 * delta * delta * (t - 4.0 / 29.0);
}
}

ColorModel::ColorModel()
{
    setIlluminant(Illuminant::D65);
}

void ColorModel::setIlluminant(Illuminant value)
{
    const Vector3 d65{0.95047, 1, 1.08883};

    Vector3 target = d65;
    if (value == Illuminant::D50)
    {
        target = {0.96422, 1, 0.82521};
    }
    if (value == Illuminant::E)
    {
        target = {1, 1, 1};
    }
    white = {100 * target[0], 100 * target[1], 100 * target[2]};

    const double x[3] = {0.64, 0.30, 0.15};

    const double y[3] = {0.33, 0.60, 0.06};

    Matrix3 primaries{};

    for (int col = 0; col < 3; ++col)
    {
        primaries[0][col] = x[col] / y[col];
        primaries[1][col] = 1;
        primaries[2][col] = (1 - x[col] - y[col]) / y[col];
    }
    Matrix3 inversePrimaries = inverse(primaries);
    Vector3 scale = multiply(inversePrimaries, d65);
    Matrix3 srgb = primaries;
    for (int row = 0; row < 3; ++row)
    {
        for (int col = 0; col < 3; ++col)
        {
            srgb[row][col] *= scale[col];
        }
    }

    const Matrix3 bradford{
        {{0.8951, 0.2664, -0.1614}, {-0.7502, 1.7135, 0.0367}, {0.0389, -0.0685, 1.0296}}};

    Vector3 sourceCone = multiply(bradford, d65);
    Vector3 targetCone = multiply(bradford, target);
    Matrix3 ratios{};

    for (int i = 0; i < 3; ++i)
    {
        ratios[i][i] = targetCone[i] / sourceCone[i];
    }
    Matrix3 inverseBradford = inverse(bradford);
    Matrix3 scaledBradford = multiply(ratios, bradford);
    Matrix3 adaptation = multiply(inverseBradford, scaledBradford);
    forward = multiply(adaptation, srgb);
    backward = inverse(forward);
}

XyzColor ColorModel::rgbToXyz(RgbColor rgb) const
{
    Vector3 v =
        multiply(forward, Vector3{removeGamma(rgb.r), removeGamma(rgb.g), removeGamma(rgb.b)});
    return {v[0] * 100, v[1] * 100, v[2] * 100};
}

RgbColor ColorModel::xyzToRgb(XyzColor xyz) const
{
    Vector3 v = multiply(backward, Vector3{xyz.x / 100, xyz.y / 100, xyz.z / 100});
    return {applyGamma(v[0]), applyGamma(v[1]), applyGamma(v[2])};
}

LabColor ColorModel::xyzToLab(XyzColor xyz) const
{
    double x = labFunction(xyz.x / white.x);
    double y = labFunction(xyz.y / white.y);
    double z = labFunction(xyz.z / white.z);
    return {116 * y - 16, 500 * (x - y), 200 * (y - z)};
}

XyzColor ColorModel::labToXyz(LabColor lab) const
{
    double y = (lab.l + 16) / 116;
    return {white.x * inverseLabFunction(y + lab.a / 500), white.y * inverseLabFunction(y),
            white.z * inverseLabFunction(y - lab.b / 200)};
}

LabColor ColorModel::rgbToLab(RgbColor rgb) const
{
    XyzColor xyz = rgbToXyz(rgb);
    return xyzToLab(xyz);
}

RgbColor ColorModel::labToRgb(LabColor lab) const
{
    XyzColor xyz = labToXyz(lab);
    return xyzToRgb(xyz);
}

CmykColor ColorModel::rgbToCmyk(RgbColor rgb, CmykMethod method)
{
    double c = 1 - rgb.r / 255;
    double m = 1 - rgb.g / 255;
    double y = 1 - rgb.b / 255;
    double gray = std::min({c, m, y});

    double k = gray;
    if (method == CmykMethod::UCR)
    {
        double strength = (gray - 0.5) / 0.5;
        strength = std::clamp(strength, 0.0, 1.0);
        k = gray * strength;
    }
    if (k >= 1 - 1e-12)
    {
        return {0, 0, 0, 1};
    }
    return {(c - k) / (1 - k), (m - k) / (1 - k), (y - k) / (1 - k), k};
}

RgbColor ColorModel::cmykToRgb(CmykColor c)
{
    return {255 * (1 - c.c) * (1 - c.k), 255 * (1 - c.m) * (1 - c.k), 255 * (1 - c.y) * (1 - c.k)};
}

RgbColor ColorModel::mapGamut(RgbColor rgb, GamutStrategy strategy, bool &changed)
{
    if (!std::isfinite(rgb.r) || !std::isfinite(rgb.g) || !std::isfinite(rgb.b))
    {
        throw std::invalid_argument("Non-finite color");
    }
    double low = std::min({rgb.r, rgb.g, rgb.b});
    double high = std::max({rgb.r, rgb.g, rgb.b});
    changed = low < -1e-7 || high > 255 + 1e-7;
    if (changed && strategy == GamutStrategy::Scaling)
    {
        double left = std::min(0.0, low);
        double right = std::max(255.0, high);
        rgb = {(rgb.r - left) * 255 / (right - left), (rgb.g - left) * 255 / (right - left),
               (rgb.b - left) * 255 / (right - left)};
    }
    return {std::clamp(rgb.r, 0.0, 255.0), std::clamp(rgb.g, 0.0, 255.0),
            std::clamp(rgb.b, 0.0, 255.0)};
}
