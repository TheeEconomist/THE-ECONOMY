import numpy as np

class UnifiedContagionSimulation:
    """
    Simulates the non-linear G-SIB network cascade cross-referencing 
    Dynamic Loss-Given-Default (LGD) matrices and Asset Fire-Sale Elasticities.
    """
    def __init__(self):
        # 29 Designated G-SIBs categorized by structural network tiers
        self.g_sibs = [
            # Tier 1: Core Hubs
            "JPM", "BAC", "C", "HSBC", "ICBC",
            # Tier 2: Clearing Conduits & Prime Brokers
            "GS", "MS", "UBS", "BNP", "BARC", "CCB",
            # Tier 3: Regional & Intermediary Nodes
            "ABC", "BOC", "BOCOM", "BKNY", "DB", "BPCE", "CACA", "ING", 
            "MZUHO", "RBC", "SAN", "SOCGEN", "STCH", "STST", "SMFG", "TD", "WFC"
        ]
        self.num_banks = len(self.g_sibs)
        
        # Asset classes and their structural fire-sale elasticities (epsilon_k)
        self.asset_classes = ["TECH", "HTM_SOV", "REAL_COMM"]
        self.elasticities = {
            "TECH": -0.75,      # Tech/AI Infrastructure: Hyper-sensitive
            "HTM_SOV": -0.32,   # Held-to-Maturity Sovereign Bonds: Duration Trap
            "REAL_COMM": -0.08  # Real Economy Commodities: Highly Inelastic
        }
        
    def initialize_system(self):
        """
        Initializes bank capital buffers, interbank exposure matrices, 
        and asset holdings using realistic relative proxy scales.
        """
        np.random.seed(42) # Ensure mathematical consistency across simulation runs
        
        # 1. Capital Buffers (K_j) in Billions of USD
        self.K = np.zeros(self.num_banks)
        self.initial_K = np.zeros(self.num_banks)
        
        # 2. Asset Holdings Portfolio (q_jk): Rows = Banks, Columns = Asset Classes
        self.q = np.zeros((self.num_banks, len(self.asset_classes)))
        
        for j, bank in enumerate(self.g_sibs):
            if j < 5:    # Tier 1 Core Hubs (Massive retail base + high capital)
                self.K[j] = np.random.uniform(180, 250)
                self.q[j] = [300, 600, 150] 
            elif j < 11: # Tier 2 Clearing Conduits (High tech/swap portfolio)
                self.K[j] = np.random.uniform(90, 140)
                self.q[j] = [650, 200, 50]  # Over-indexed into Tech collateral
            else:        # Tier 3 Regional Nodes (Leaner buffers, standard sovereign weight)
                self.K[j] = np.random.uniform(45, 85)
                self.q[j] = [100, 250, 80]
                
        self.initial_K = self.K.copy()
        
        # 3. Interbank Gross Exposure Matrix x_ij (Row i owes Column j)
        self.x = np.zeros((self.num_banks, self.num_banks))
        for i in range(self.num_banks):
            for j in range(self.num_banks):
                if i != j:
                    if i >= 5 and i < 11 and j < 5: 
                        # Tier 2 owes Tier 1 via repo channels
                        self.x[i, j] = np.random.uniform(35, 75)
                    elif i >= 11 and j >= 5 and j < 11:
                        # Tier 3 owes Tier 2 via prime broker funding
                        self.x[i, j] = np.random.uniform(15, 35)
                    else:
                        # Baseline residual interbank noise
                        self.x[i, j] = np.random.uniform(2, 10)
                        
        # 4. Initialize dynamic state variables
        self.alpha = {"TECH": 0.0, "HTM_SOV": 0.0, "REAL_COMM": 0.0} # Price drops
        self.bank_default_status = np.zeros(self.num_banks, dtype=bool) # Insolvency flags
        
    def execute_cascade_step(self, iteration):
        """
        Executes a single discrete step inside the unified non-linear contagion loop.
        """
        new_defaults = False
        forced_sales = {"TECH": 0.0, "HTM_SOV": 0.0, "REAL_COMM": 0.0}
        
        # Dynamic LGD matrix lookup update (Lambda_ij)
        Lambda = np.full((self.num_banks, self.num_banks), 0.45) # Baseline historical unsecured LGD
        
        # Tech collateral degradation drives LGD higher for Tier 2 loans
        tech_degradation_factor = max(0.0, 1.0 + self.alpha["TECH"])
        for i in range(self.num_banks):
            for j in range(self.num_banks):
                if i >= 5 and i < 11 and j < 5: # Tier 2 to Tier 1 loans
                    # Collateral cover fails, moving LGD towards 0.95 unsecured ceiling
                    if tech_degradation_factor < 0.65:
                        Lambda[i, j] = 0.45 + 0.50 * (1.0 - tech_degradation_factor)
        
        # Track previous capital states to isolate marginal iteration loss
        K_prev = self.K.copy()
        
        for j in range(self.num_banks):
            if self.bank_default_status[j]:
                continue # Bank already cleared and halted
                
            # Channel 1: Interbank Network Default Transmission
            interbank_loss = 0.0
            for i in range(self.num_banks):
                if self.bank_default_status[i]: # If counterparty i is insolvent
                    interbank_loss += Lambda[i, j] * self.x[i, j]
            
            # Channel 2: Systemic Asset Devaluation (Impact of current alpha vector)
            asset_loss = 0.0
            for k_idx, k in enumerate(self.asset_classes):
                # Loss is proportional to the total valuation shift from baseline
                asset_loss += -self.alpha[k] * self.q[j, k_idx]
                
            # Apply total structural subtraction to capital buffer
            self.K[j] = max(0.0, self.initial_K[j] - interbank_loss - asset_loss)
            
            # Check Insolvency Tipping Boundary Condition (K_j <= 0)
            if self.K[j] <= 0.0 and not self.bank_default_status[j]:
                self.bank_default_status[j] = True
                new_defaults = True
                
                # Liquidation Trigger: Insolvent banks dump asset blocks to clear lines
                # Tier 2 dumps tech instantly; Tier 1/3 dump sovereign portfolios to stem cash drains
                if j >= 5 and j < 11:
                    forced_sales["TECH"] += self.q[j, 0] * 0.85
                    forced_sales["HTM_SOV"] += self.q[j, 1] * 0.40
                else:
                    forced_sales["HTM_SOV"] += self.q[j, 1] * 0.75
                    forced_sales["REAL_COMM"] += self.q[j, 2] * 0.20
                    
        # Update Price Elasticity vectors based on forced liquidation volumes
        for k in self.asset_classes:
            if forced_sales[k] > 0.0:
                # Non-linear exponential degradation equation
                total_volume_scaled = forced_sales[k] / 10000.0 # Scale volume metric
                self.alpha[k] = np.exp(self.elasticities[k] * total_volume_scaled) - 1.0
                
        return new_defaults

    def run_simulation(self):
        """
        Runs the full contagion engine from the initial shock phase 
        until the network reaches a steady-state resolution.
        """
        self.initialize_system()
        
        print("=" * 95)
        print("INITIALIZING G-SIB NON-LINEAR CONTAGION ENGINE (2055 BREACH GATE)")
        print("=" * 95)
        print(f"Total Bank Nodes Tracked:    {self.num_banks} Global Systemically Important Banks")
        print(f"Initial Aggregate Capital:   ${np.sum(self.K):.2f} Billion")
        print("-" * 95)
        
        # Induction Shock: Initial 35% liquidation drop hits Tech sector collateral
        print("[SHOCK PHASE]: Initializing Concentration Trap Collapse Vector...")
        self.alpha["TECH"] = -0.35
        self.alpha["HTM_SOV"] = -0.05
        
        iteration = 1
        system_active = True
        
        while system_active and iteration <= 6:
            print(f"\n--- Cascade Iteration Loop Step {iteration} ---")
            new_failures = self.execute_cascade_step(iteration)
            
            # Print state parameters
            active_defaults = [self.g_sibs[idx] for idx, status in enumerate(self.bank_default_status) if status]
            print(f"  Insolvent G-SIB Count: {len(active_defaults)} / 29 Nodes")
            print(f"  Active Insolvent List: {active_defaults if active_defaults else 'None'}")
            print(f"  Asset Devaluation Base | TECH: {self.alpha['TECH']*100:.1f}% | HTM_SOV: {self.alpha['HTM_SOV']*100:.1f}% | REAL_COMM: {self.alpha['REAL_COMM']*100:.1f}%")
            print(f"  Remaining System Capital Pool: ${np.sum(self.K):.2f} Billion")
            
            if not new_failures:
                print("\n[STEADY-STATE]: Network contagion halted. No further node tipping registered.")
                system_active = False
            iteration += 1
            
        print("=" * 95)
        print("SYSTEMIC RESET TERMINUS COMPLETE")
        print("=" * 95)
        print(f"Final Insolvent Nodes:   {np.sum(self.bank_default_status)} banks completely liquidated.")
        print(f"Surviving Capital Ratio: {(np.sum(self.K)/np.sum(self.initial_K))*100:.2f}% of baseline remaining.")
        print("System Execution Status: Ready for Controlled Value Clearing Protocol realignment.")
        print("=" * 95)

if __name__ == "__main__":
    sim = UnifiedContagionSimulation()
    sim.run_simulation()
