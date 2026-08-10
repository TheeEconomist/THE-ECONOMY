import numpy as np

def debt_dynamics_decomposition(primary_balances, interest_rates, growth_rates, 
                                initial_debt_ratio, inflation_erosion=None):
    """
    Decomposes the change in debt-to-GDP ratio into:
    - Primary surplus contribution (true repayment)
    - Interest-growth differential
    - Inflation / financial-repression erosion (optional)
    
    Returns the fraction of the debt reduction that was NEVER repaid 
    in real purchasing power (i.e., was grown or inflated away).
    """
    
    n = len(primary_balances)
    d = np.zeros(n + 1)
    d[0] = initial_debt_ratio
    
    primary_contrib = 0.0
    r_g_contrib = 0.0
    inflation_contrib = 0.0
    
    for t in range(n):
        pb = primary_balances[t]
        r = interest_rates[t]
        g = growth_rates[t]
        
        # Standard approximate debt dynamics
        delta_d = (r - g) * d[t] - pb
        
        # Optional explicit inflation erosion term
        if inflation_erosion is not None:
            infl = inflation_erosion[t]
            delta_d -= infl * d[t]          # inflation reduces real burden
            inflation_contrib += infl * d[t]
        
        d[t+1] = d[t] + delta_d
        
        primary_contrib += pb               # positive pb reduces debt
        r_g_contrib += (r - g) * d[t]
    
    total_change = d[-1] - d[0]             # should be negative for reduction
    
    # Fraction never repaid in real purchasing power
    if total_change < 0:
        repaid_fraction = primary_contrib / abs(total_change)
        never_repaid_fraction = 1.0 - repaid_fraction
    else:
        repaid_fraction = 0.0
        never_repaid_fraction = 1.0
    
    results = {
        "initial_debt_ratio": d[0],
        "final_debt_ratio": d[-1],
        "total_change": total_change,
        "primary_surplus_contribution": primary_contrib,
        "interest_growth_contribution": r_g_contrib,
        "inflation_contribution": inflation_contrib,
        "repaid_fraction": repaid_fraction,
        "never_repaid_fraction": never_repaid_fraction
    }
    
    return results, d


# ============================================================
# Example: Stylized Post-WWII U.S. Case (1946–1974)
# ============================================================

if __name__ == "__main__":
    
    # Simplified illustrative series (annual averages for demonstration)
    # In a full historical reconstruction these would be year-by-year data
    
    years = 28  # 1946 to 1974
    
    # Average primary surplus ~0.9% of GDP (literature range)
    primary_balances = np.full(years, 0.009)
    
    # Approximate average r and g consistent with historical decompositions
    interest_rates = np.full(years, 0.03)      # nominal effective rate
    growth_rates   = np.full(years, 0.07)      # nominal GDP growth (real + inflation)
    
    # Optional mild inflation erosion term
    inflation_erosion = np.full(years, 0.015)
    
    initial_d = 1.06   # 106% of GDP
    
    results, path = debt_dynamics_decomposition(
        primary_balances,
        interest_rates,
        growth_rates,
        initial_d,
        inflation_erosion
    )
    
    print("=" * 65)
    print("DEBT DECOMPOSITION & NON-REPAID FRACTION")
    print("=" * 65)
    print(f"Initial debt/GDP:             {results['initial_debt_ratio']:.3f}")
    print(f"Final debt/GDP:               {results['final_debt_ratio']:.3f}")
    print(f"Total change:                 {results['total_change']:.3f}")
    print("-" * 65)
    print(f"Primary surplus contribution: {results['primary_surplus_contribution']:.3f}")
    print(f"Interest-growth contribution: {results['interest_growth_contribution']:.3f}")
    print(f"Inflation erosion:            {results['inflation_contribution']:.3f}")
    print("-" * 65)
    print(f"Repaid fraction (true):       {results['repaid_fraction']:.1%}")
    print(f"Never repaid in real terms:   {results['never_repaid_fraction']:.1%}")
    print("=" * 65)
    print("\nInterpretation:")
    print("Even in this favorable historical stylized case, the majority of the")
    print("debt-ratio reduction was NOT achieved by primary surpluses (true repayment).")
    print("Most of the claims were grown away or inflated away.")
