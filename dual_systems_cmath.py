using System;

public static class DualSystemEquations
{
    // 1. Core Debt Dynamics
    public static double DeltaDebtRatio(double dPrev, double r, double g, double pb)
    {
        return (r - g) * dPrev - pb;
    }

    // 4. Mitigation Term
    public static double Mitigation(double DPrev, double r, double g, double pi, double kappa)
    {
        double growthTerm = Math.Max(0.0, g - r);
        return (growthTerm + kappa * pi) * DPrev;
    }

    // 6. Effective Residual Addition
    public static double EffectiveResidual(double C, double rho, double DPrev, double r, double g,
                                           double pi, double kappa, double psiBucket)
    {
        return C * (1.0 - rho) + (psiBucket - Math.Max(0.0, g - r) - kappa * pi) * DPrev;
    }

    // 7. Reciprocal Mirror
    public static double ReciprocalMirror(double lambda)
    {
        return 1.0 / lambda;
    }

    // 8. Dynamic Collateral Quality
    public static double DynamicOmega(double omega0, double omegaMin, double Mt, double M0, double gamma)
    {
        double ratio = Mt / M0;
        return omegaMin + (omega0 - omegaMin) * Math.Pow(ratio, gamma);
    }

    // 9. Endogenous Overshoot Severity
    public static double OvershootSeverity(double val, double Ceff, double alpha)
    {
        return alpha * Math.Max(0.0, val / Ceff - 1.0);
    }

    // 10. Equity Path Operator
    public static double EquityPath(double PPrev, double delta, double omega, bool crossed)
    {
        return crossed ? PPrev * (1.0 - delta * omega) : PPrev;
    }

    // 11. Terminal Clearing Operator
    public static double TerminalClearing(double PPrev, double omega, double weightedSum, double Dt)
    {
        return (PPrev * omega / weightedSum) * Dt;
    }

    // 13. Capacity Breach
    public static bool IsBreach(double val, double M)
    {
        double Ceff = 3.65 * M;
        return val > Ceff;
    }
}
