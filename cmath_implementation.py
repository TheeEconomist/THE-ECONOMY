#include <algorithm>
#include <cmath>

class DualSystemEquations {
public:
    // 1. Core Debt Dynamics
    static double deltaDebtRatio(double dPrev, double r, double g, double pb) {
        return (r - g) * dPrev - pb;
    }

    // 4. Mitigation Term
    static double mitigation(double DPrev, double r, double g, double pi, double kappa) {
        double growthTerm = std::max(0.0, g - r);
        return (growthTerm + kappa * pi) * DPrev;
    }

    // 6. Effective Residual Addition
    static double effectiveResidual(double C, double rho, double DPrev, double r, double g,
                                    double pi, double kappa, double psiBucket) {
        return C * (1.0 - rho) + (psiBucket - std::max(0.0, g - r) - kappa * pi) * DPrev;
    }

    // 7. Reciprocal Mirror
    static double reciprocalMirror(double lambda) {
        return 1.0 / lambda;
    }

    // 8. Dynamic Collateral Quality
    static double dynamicOmega(double omega0, double omegaMin, double Mt, double M0, double gamma) {
        double ratio = Mt / M0;
        return omegaMin + (omega0 - omegaMin) * std::pow(ratio, gamma);
    }

    // 9. Endogenous Overshoot Severity
    static double overshootSeverity(double val, double Ceff, double alpha) {
        return alpha * std::max(0.0, val / Ceff - 1.0);
    }

    // 10. Equity Path Operator
    static double equityPath(double PPrev, double delta, double omega, bool crossed) {
        return crossed ? PPrev * (1.0 - delta * omega) : PPrev;
    }

    // 11. Terminal Clearing Operator
    static double terminalClearing(double PPrev, double omega, double weightedSum, double Dt) {
        return (PPrev * omega / weightedSum) * Dt;
    }

    // 13. Capacity Breach
    static bool isBreach(double val, double M) {
        double Ceff = 3.65 * M;
        return val > Ceff;
    }
};
