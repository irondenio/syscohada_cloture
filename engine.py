import pandas as pd
import numpy as np

def process_balance(df):
    """
    Processes a SYSCOHADA Trial Balance for a large Industrial Enterprise.
    Enhanced mapping for classes 1-8.
    """
    df['Débit'] = pd.to_numeric(df['Débit'], errors='coerce').fillna(0)
    df['Crédit'] = pd.to_numeric(df['Crédit'], errors='coerce').fillna(0)
    df['Balance'] = df['Débit'] - df['Crédit']
    
    # helper for specific account range
    def get_bal(prefixes):
        return df[df['Compte'].astype(str).str.startswith(tuple(prefixes))]['Balance'].sum()
    
    # Indicators based on SYSCOHADA
    revenue = -df[df['Compte'].astype(str).str.startswith('70')]['Balance'].sum()
    other_income = -df[df['Compte'].astype(str).str.startswith(('71', '72', '75'))]['Balance'].sum()
    total_revenue = revenue + other_income
    
    raw_materials = df[df['Compte'].astype(str).str.startswith('601')]['Balance'].sum()
    external_services = df[df['Compte'].astype(str).str.startswith(('61', '62', '63'))]['Balance'].sum()
    personnel = df[df['Compte'].astype(str).str.startswith('66')]['Balance'].sum()
    taxes = df[df['Compte'].astype(str).str.startswith('64')]['Balance'].sum()
    
    ebitda = total_revenue - (raw_materials + external_services + personnel + taxes)
    depreciation = df[df['Compte'].astype(str).str.startswith('68')]['Balance'].sum()
    ebit = ebitda - depreciation
    
    financial_exp = df[df['Compte'].astype(str).str.startswith('67')]['Balance'].sum()
    financial_inc = -df[df['Compte'].astype(str).str.startswith('77')]['Balance'].sum()
    
    net_profit = ebit + financial_inc - financial_exp
    
    fixed_assets = get_bal(['2'])
    inventory = get_bal(['3'])
    receivables = get_bal(['41'])
    cash = get_bal(['5'])
    total_assets = fixed_assets + inventory + receivables + cash
    
    equity = -get_bal(['10', '11', '12', '13'])
    long_term_debt = -get_bal(['16'])
    payables = -get_bal(['40'])
    
    working_capital = (equity + long_term_debt) - fixed_assets
    
    return {
        "revenue": revenue,
        "total_revenue": total_revenue,
        "ebitda": ebitda,
        "ebit": ebit,
        "net_profit": net_profit,
        "fixed_assets": fixed_assets,
        "inventory": inventory,
        "cash": cash,
        "equity": equity,
        "debt": long_term_debt,
        "working_capital": working_capital,
        "total_assets": total_assets,
        "maintenance_costs": df[df['Compte'].astype(str).str.startswith('615')]['Balance'].sum()
    }

def get_sample_data():
    """ Elaborated Industrial Enterprise Trial Balance """
    data = {
        'Compte': [
            '101', '111', '161', # Equity & Debt
            '211', '213', '215', '218', # Fixed Assets (Land, Buildings, Machines, Transp)
            '311', '351', # Inventory (Raw materials, Finished goods)
            '411', '401', '421', # Third parties
            '521', '571', # Cash (Bank, Petit cash)
            '601', '602', '603', # Purchases
            '615', '622', '632', # External services (Maintenance, Fees, Transport)
            '641', '644', # Taxes
            '661', '667', # Personnel
            '681', # Depreciation
            '701', '707', # Sales
            '711', # Change in inventory
        ],
        'Libellé': [
            'Capital Social', 'Réserves', 'Emprunts LMT',
            'Terrains', 'Constructions', 'Instal. Tech & Machines', 'Matériel Transport',
            'Stock Matières Premières', 'Stock Produits Finis',
            'Clients', 'Fournisseurs', 'Personnel - Rémunérations',
            'Banque Centrale', 'Caisse',
            'Achats de MP', 'Achats Fournitures', 'Var. Stock MP',
            'Entretien & Réparations', 'Honoraires', 'Transports',
            'Impôts & Taxes', 'Taxes sur CA',
            'Rémunérations Personnel', 'Charges Sociales',
            'Dotations Amortissements',
            'Ventes Produits Finis', 'Ventes Marchandises',
            'Production Stockée'
        ],
        'Débit': [
            0, 0, 0,
            250000000, 450000000, 850000000, 120000000,
            85000000, 140000000,
            115000000, 0, 0,
            45000000, 5000000,
            415000000, 25000000, 0,
            75000000, 35000000, 55000000,
            12000000, 8000000,
            145000000, 55000000,
            85000000,
            0, 0,
            0
        ],
        'Crédit': [
            1000000000, 250000000, 450000000,
            0, 0, 0, 0,
            0, 0,
            0, 115000000, 65000000,
            0, 0,
            0, 0, 15000000,
            0, 0, 0,
            0, 0,
            0, 0,
            0,
            1150000000, 85000000,
            125000000
        ]
    }
    return pd.DataFrame(data)
