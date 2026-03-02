import pandas as pd
import numpy as np

def process_balance(df):
    """
    Processes a SYSCOHADA Trial Balance (Balance de vérification).
    Expected columns: Compte, Libellé, Débit, Crédit
    """
    # Simple mapping logic for POC (SYSCOHADA)
    # Class 1: Equity/Long-term debt
    # Class 2: Fixed Assets
    # Class 3: Inventory
    # Class 4: Third parties (Accounts receivable/payable)
    # Class 5: Cash & Banks
    # Class 6: Expenses
    # Class 7: Revenues
    
    # Ensure numeric
    df['Débit'] = pd.to_numeric(df['Débit'], errors='coerce').fillna(0)
    df['Crédit'] = pd.to_numeric(df['Crédit'], errors='coerce').fillna(0)
    df['Balance'] = df['Débit'] - df['Crédit']
    
    # Mapping
    results = {
        "revenue": df[df['Compte'].astype(str).str.startswith('7')]['Crédit'].sum() - df[df['Compte'].astype(str).str.startswith('7')]['Débit'].sum(),
        "expenses": df[df['Compte'].astype(str).str.startswith('6')]['Débit'].sum() - df[df['Compte'].astype(str).str.startswith('6')]['Crédit'].sum(),
        "fixed_assets": df[df['Compte'].astype(str).str.startswith('2')]['Balance'].sum(),
        "current_assets": df[df['Compte'].astype(str).str.startswith(('3', '4', '5'))]['Balance'].sum(),
        "equity_debt": -df[df['Compte'].astype(str).str.startswith('1')]['Balance'].sum(),
        "cash": df[df['Compte'].astype(str).str.startswith('5')]['Balance'].sum()
    }
    
    results['net_profit'] = results['revenue'] - results['expenses']
    results['working_capital'] = results['equity_debt'] - results['fixed_assets']
    
    return results

def get_sample_data():
    data = {
        'Compte': ['101', '161', '211', '311', '411', '401', '521', '601', '701'],
        'Libellé': ['Capital', 'Emprunts', 'Terrains', 'Marchandises', 'Clients', 'Fournisseurs', 'Banque', 'Achats', 'Ventes'],
        'Débit': [0, 0, 50000, 15000, 20000, 0, 10000, 35000, 0],
        'Crédit': [40000, 10000, 0, 0, 0, 15000, 0, 0, 65000]
    }
    return pd.DataFrame(data)
