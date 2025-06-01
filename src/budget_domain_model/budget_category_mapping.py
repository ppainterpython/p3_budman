# ---------------------------------------------------------------------------- +
#region category_mapping.py module
""" Functions enabling mapping of FI transactions to budget categories.

"""
#endregion p3_execl_budget.p3_banking_transactions budget_transactions.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
import re, pathlib as Path, logging

# third-party modules and packages
import p3logging as p3l, p3_utils as p3u
from openpyxl import Workbook, load_workbook

# local modules and packages.
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region Category Map
# Map values to column ['Category'] by re pattern-matching to 
# column ['Original Description'].
# This list of patterns will be quite long. 
# TODO: How to use data to train an LLM or ML model to do this?
category_map = {
    # Donations
    r'(?i)\bCAMPUS\s\bCRUSADE\b': 'Charity.Campus Crusade',
    r'(?i)\bTUNNELTOTOWERS\b': 'Charity.Tunnel to Towers',
    r'(?i)\bFOCUS\sON\sTHE\sFAMILY\b': 'Charity.Focus on the Family',
    r'(?i)\bPioneers\sBlueChe\b': 'Charity.Pioneers',
    r'(?i)\bST\sJUDE\b': 'Charity.St. Jude',
    r'(?i)\bWorld\s*Vision\s*Inc\b': 'Charity.World Vision',
    r'(?i)\bID:GOFUNDME\sJOHN\sW\b': 'Donation.GoFundMe.John Wick',
    r'(?i)\bWINRED\*\s*NRSC\b': 'Donation.Republican Party',
    # Housing, Utilities etc.
    r'(?i)\bReliant\sEnergy\b': 'Grape Cove.Utilities.Electric',
    r'(?i)\bPedernales_Elec\b': 'Castle Pines.Utilities.Electric',
    r'(?i)\bONE\sGAS\b': 'Grape Cove.Utilities.Natural Gas',
    r'(?i)\bATMOS\sENERGY\b': 'Grape Cove.Utilities.Natural Gas',
    r'(?i)\bService\sExperts\b': 'Grape Cove.Maintenance.HVAC',
    r'(?i)\bBrushy\sCreek\sMUD\b': 'Grape Cove.Utilities.MUD',
    r'(?i)\bAT\&T\sU-Verse\b': 'Grape Cove.Telecom.ATT U-Verse',
    r'(?i)\bGoogle\sFIBER\b': 'Castle Pines.Telecom.Google Fiber',
    r'(?i)\bGoogle\s*\*FIBER\b': 'Castle Pines.Telecom.Google Fiber',
    r'(?i)\bCity\sof\sAustin\b': 'Castle Pines.Utilities.City of Austin',
    r'(?i)\bGOOGLE\s\*FIBER\b': 'Castle Pines.Internet.Google Fiber',
    r'(?i)\bavery\W*.*?\branch\W*.*?\bHOA\W*.*?\bdues\b': 'Castle Pines.HOA',
    r'(?i)\bFREDERICK\sPEVA\b': 'Housing.Lawn Care',
    r'(?i)\bTRUGREEN\b': 'Housing.TruGreen',
    r'(?i)\bTRANSFER\s*PAUL\s*B\s*PAINTER\s*LAURA:john\s*hogge\b': 'Housing.Mortgage',
    r'(?i)\bTHE\sHOME\sDEPOT\b': 'Housing.Maintenance',
    r"(?i)\bLOWE's\b": 'Housing.Maintenance',
    r'(?i)\bCASHWAY\sBLDG\sMATERIALS\b': 'Housing.Maintenance',
    r'(?i)\bCULLIGAN\b': 'Grape Cove.Culligan',
    r'(?i)\bCULLINGAN\b': 'Grape Cove.Culligan',
    r'(?i)\bRIGHTSPACE\sSTORAGE\b': 'Housing.Storage Unit',
    r'(?i)\bATT\b': 'Telecom.Cellular',
    r'(?i)\bVZ\sWIRELESS\sVE': 'Telecom.Verizon',
    r'(?i)\bFSP\*ABC\sHOME\s&\sCOMMERCIAL': 'Housing.Pest Control',
    r'(?i)\bRING\sBASIC\sPLAN\b': 'Castle Pines.Ring Security Service',
    r'(?i)\bSTRAND\sBROTHERS\sSERVICE\b': 'Castle Pines.Maintenance.HVAC',
    r'(?i)\bWHITTLESEY\sLANDSCAPE-11\s': 'Housing.Lawn Care',
    r'(?i)\bTHE\sGRASS\sOUTLET': 'Housing.Lawn Care',
    r'(?i)\bJack\sBrown\sCleaners': 'Housing.Dry Cleaning',
    # Auto
    r'(?i)\bDISCOUNT-TIRE-CO\b': 'Auto.Tires',
    r"(?i)\bO'REILLY\b": "Auto.Maintenance.O'Reilly",
    r'(?i)\bCHEVRON\b': 'Auto.Gasoline.Chevron',
    r'(?i)\bGO\s\bCARWASH\b': 'Auto.Carwash.Go Carwash',
    r'(?i)\bHCTRA\sEFT\b': 'Auto.Tolls.HCTRA',
    r'(?i)\bdoxoPLUS\b': 'Auto.Tolls.DoxoPlus',
    r'(?i)\bRMA\sTOLL\b': 'Auto.Tolls.RMA',
    # Groceries
    r'(?i)\bTARGET\b': 'Groceries.H-E-B Pharmacy',
    r'(?i)\bSAMS\s*CLUB\b': "Groceries.Sam's Club",
    r'(?i)\bDOLLAR\sGENERAL\b': 'Groceries.Dollar General',
    r'(?i)\bCOSTCO\sWHSE\b': 'Groceries.CostCo',
    r'(?i)\bH-E-B\b': 'Groceries.H-E-B',
    r'(?i)\bQT\b': 'Groceries.QT',
    r'(?i)\bTWIN\sLIQUORS\b': 'Groceries.Liquor',
    # Insurance
    r'(?i)\bPRINCIPAL-CCA\b': 'Insurance.Principal Life Insurance',
    r'(?i)\bHP\s*\bDES:INS\sPREM\b': 'Insurance.Cobra Medical',
    r'(?i)\bState\s\bFARM\b': 'Insurance.State Farm',
    r'(?i)\bTexas\s*Law\b': 'Insurance.Texas Law',
    # Medical
    r'(?i)\bGEORGETOWN\sOB-GYN\b': 'Medical.Bio-T',
    r'(?i)\bQDI\*QUEST\sDIAGNOSTICS\b': 'Medical.Labs',
    r'(?i)\bHAROLD\sF\sADELMAN\sMD\b': 'Medical.Adelman',
    r'(?i)\bBSWHealth.*\b': 'Medical.BSW Health',
    r'(?i)\bJOHN\sF\sLANN\sDDS\b': 'Dental.Lann',
    r'(?i)\bCVS/PHARM\b': 'Medical.Pharmacy.CVS',
    r'(?i)\bCAREMARK\sMAIL\b': 'Medical.Pharmacy.CVS',
    r'(?i)\bWWW\.CAREMARK\.COM\b': 'Medical.Pharmacy.CVS',
    r'(?i)\bCVS.*PHARMACY\b': 'Medical.Pharmacy.CVS',
    r'(?i)\bMINUTECLINIC\b': 'Medical.Pharmacy.CVS Minute Clinic',
    # Health and Fitness, Coaching
    r'(?i)\bID:23ANDME\sINC\b': 'Health and Fitness.23andMe',
    r'(?i)\bFINLEYS\sAVERY\sRANCH\b': 'Health and Fitness.Haircut Paul',
    r'(?i)\bCATHY\s\bDUNFORD\b': 'Health and Fitness.Coach Cathy',
    r'(?i)\bSNICOLA\s\bMCKERLIE\b': 'Health and Fitness.Nicola McKerlie',
    r'(?i)\bQuest\s*Diagnostic\s': 'Health and Fitness.Lab Work',
    r'(?i)\bLABORATORY\s*CORPORATION\s': 'Health and Fitness.Lab Work',
    r'(?i)\bNEW\s*TECH\s*TENNIS': 'Health and Fitness.Tennis',
    # Streaming and Subscriptions
    r'(?i)\bID:ANCESTO*RYCOM\b': 'Subscription.Ancestry-com',
    r'(?i).*TEAMVIEWER.*': 'Subscription.TeamViewer',
    r'(?i)\bSXM\*SIRIUSXM\.COM/ACCT\b': 'Subscription.SiriusXM',
    r'(?i)\bID:ADOBE\sINC\b': 'Subscription.Adobe',
    r'(?i)\bCINEMARK\b': 'Theater.Cinemark',
    r'(?i)\bAudible\*.*\b': 'Subscription.Audible',
    r'(?i)\bID:ANGIES\sLIST\b': 'Subscription.Angies List',
    r'(?i)\bID:GITHUB\sINC\b': 'Subscription.GitHub',
    r'(?i)\bID:HULU\b': 'Subscription.Hulu',
    r'(?i)\bID:PATREON\s*MEMBER\b': 'Subscription.Patreon',
    r'(?i)\bPrime\s\bVideo\b': 'Subscription.Amazon Prime Video',
    r'(?i)\bTHIRTEEN\b': 'Subscription.Thirteen',
    r'(?i)\bID:NETFLIX\.COM\b': 'Subscription.Netflix',
    r'(?i)\bID:DROPBOX\b': 'Subscription.DropBox',
    r'(?i)\bwikimedia\b': 'Subscription.WikiPedia',
    r'(?i)\bPAYPAL\b.*ID:CLEVERBRIDG': 'Subscription.Software',
    r'(?i)\bCHECKCARD\b.*APPLE\sCOM\sBILL': 'Subscription.Apple',
    # Restaurants, Door Dash, Eating Out, Snacks
    r'(?i)\bID:STARBUCKS\b': 'Restaurants.Starbucks',
    r'(?i)\bSAVERS\b': 'Restaurants.Savers',
    r"(?i)\b183\sPHIL's\b": "Restaurants.183 Phil's",
    r'(?i)\s\*SMOKEY\sMOS\sBBQ\b': "Restaurants.Smokey Mo's BBQ",
    r'(?i)\bTST\*LA\sMARGARITA\b': 'Restaurants.La Margarita',
    r'(?i)\bSURF\sAND\sTURF\b': 'Restaurants.Surf and Turf',
    r'(?i)\bCASA\sOLE\b': 'Restaurants.Casa Ole',
    r'(?i)\bID:DOORDASH\b': 'Restaurants.Door Dash',
    r'(?i)\bID:DOORDASHINC\b': 'Restaurants.Door Dash',
    r'(?i)\s\*DOORDASH\b': 'Restaurants.Door Dash',
    r'(?i)\bDAIRY\sQUEEN\b': 'Restaurants.Dairy Queen',
    r'(?i)\bCHICK-FIL-A\b': 'Restaurants.Chick-Fil-A',
    r'(?i)\bMOD\sPIZZA\b': 'Restaurants.Mod Pizza',
    r"(?i)\bMCDONALD'S\b": "Restaurants.McDonald's",
    r"(?i)\bMANDOLAS\b": "Restaurants.McDonald's",
    r'(?i)\bTHE\s*LEAGUE\s*KITCHEN\b': 'Restaurants.The League Kitchen',
    r"(?i)\bTONY\sC'S\sCOAL\sFIRED\b": "Restaurants.Tony C's Coal Fired",
    r'(?i)\bTST\*SANTIAGOS\s*TEX\s*MEX\b': 'Restaurants.Santiagos Tex Mex',
    r'(?i)\bPOTBELLY\s': 'Restaurants.PotBelly',
    # Shopping - Amazon, Apple, etc.
    r'(?i)\bID:RUNNINGWARE\b': 'Shopping.Clothing.Running Warehouse',
    r'(?i)\bID:UNDERWATER\sUNDE\b': 'Shopping.Apple',
    r'(?i)\bID:LAGOSEC\sINC\b': 'Unknown.Lagosec',
    r'(?i)\bID:FASTSPRING\b': 'Shopping.FastSpring',
    r'(?i)\bMICROSOFT\b': 'Shopping.Microsoft',    
    r'(?i)\bETSY,\sINC\.': 'Shopping.Etsy',
    r'(?i)\bBARNES\s&\sNOBLE\b': 'Shopping.Barnes & Noble',
    r'(?i)\bBASS\sPRO\sSTORE\b': 'Shopping.Bass Pro',
    r'(?i)\bAT\sHOME\b': 'Shopping.At Home',
    r'(?i)\bAMAZON\s.*?\bPRIME\b': 'Shopping.Amazon Prime',
    r'(?i)\bAMAZON\sRETA\*\s\b': 'Shopping.Amazon Retail',
    r'(?i)\bAMAZON\s\bMKTPL\*.*\b': 'Shopping.Amazon Marketplace',
    r'(?i)\bAMAZON\.com\*.*\b': 'Shopping.Amazon',
    r'(?i)\bAMAZON\s(MARKETPLA\s|MKTPLACE\s)\b': 'Shopping.Amazon Marketplace',
    r'(?i)\bAMAZON\s\b(DIGITAL|DIGI).*?\b(LINKEDIN|LINKWA)\b': 'Shopping.Amazon Digital',
    r'(?i)\bAMAZON\s\b(DIGITAL|DIGI).*': 'Shopping.Amazon Digital',
    r'(?i)\b.*APPLE\.COM.*\b': 'Shopping.Apple',
    r'(?i)\bCIRCLE\sK\b': 'Shopping.Circle K',
    r'(?i)\b7-ELEVEN\s.*?MOBILE\sPURCHASE\b': 'vape',
    r'(?i)\b7-ELEVEN\b': 'Shopping.7-Eleven',
    r'(?i)\bMICHAELS\sSTORES\b': 'Shopping.Michaels',
    r'(?i)\bWALGREENS\s*(STORE)*\b': 'Shopping.Walgreens',
    r'(?i)\bPAYPAL\s*(STORE)*\b': 'Shopping.Walgreens',
    r'(?i)\bPAYPAL\s': 'Shopping.PayPal',
    r'(?i)\bSMART\sSTOP': 'Shopping.Misc',
    # Pets
    r'(?i)\bPETSUITES\sGREAT\sOAKS\b': 'Pets.Boarding',
    r'(?i)\bGREAT\sOAKS\sANIMAL\b': 'Pets.Veterinary',
    r'(?i)\bID:CHEWY\sINC\b': 'Pets.Dog Food',
    # Professional and Historical Organizations
    r'(?i)\bID:INSTITUTEEL\b': 'Professional.IEEE',
    # Work-related Expenses
    r'(?i)\b.*ZOOMCOMM.*\b': 'Subscription.Zoom',
    r'(?i)\bVISUALMIND\s*APP\b': 'Work-related.VisualMind',
    r'(?i)\bEXECUTIVE\sCAREER\sUPGRA\b': 'Work-related.ECU Recruiting',
    r'(?i)\bOTTER\.AI\b': 'Work-related.OTTER-AI',
    r'(?i)\bID:LINKEDIN\b': 'Work-related.Linked In',
    r'(?i)esferas.io': 'Work-related.ECU Recruiting',
    # Income
    r'(?i)\bInterest\sEarned\b': 'Income.Interest',
    r'(?i)\bGerson\sLehrman\sG\b': 'Income.Consulting.GL Group',
    r'(?i)\bHP\sINC*?\bPAYROLL\b': 'Income.HP Inc',
    r'(?i)\bHP\sINC\.\s*\bDES:PAYROLL\b': 'Income.HP Inc',
    r'(?i)\bTWC-BENEFITS\b': 'Income.TWC.',
    r'(?i)\bBank\s*of\s*America.*CASHREWARD': 'Income.Bank Reward',
    # Banking, Finance and Taxes 
    r'(?i)\bCheck\s*x*\d*\b': 'Banking.Checks to Categorize',
    r'(?i)\bPreferred\s*Rewards.*\b': 'Banking.Preferred Rewards',
    r'(?i)\bWILLIAMSON\s*COUNT\s*DES:EPAYMENT\b': 'Taxes.Williamson County',  
    r'(?i)\bPMT\*WILCO\sTAX\b': 'Taxes.Williamson County',
    r'(?i)\bLATE\sFEE\sFOR\sPAYMENT\sDUE\b': 'Banking.Late Fee',
    r'(?i)\bINTEREST\sCHARGED\sON\sPURCHASES\b': 'Banking.Interest',
    r'(?i)\bFRAUD\sDISPUTE\b': 'Banking.Fraud Dispute',
    r'(?i)\bGB\sREVERS(AL|ED)\b': 'Banking.Fraud Dispute',
    r'(?i)\bFOREIGN\sTRANSACTION\sFEE\b': 'Banking.Foreign Transaction Fee',
    r'(?i)\bExperian\*\sCredit\sReport\b': 'Finance.Experian',
    r'(?i)\bBKOFAMERICA\sATM.*\bWITHDRWL\b': 'Banking.ATM',
    r'(?i)\bBKOFAMERICA\sMOBILE.*\bDEPOSIT\b': 'Banking.Mobile Deposit',
    r'(?i)\bGITKRAKEN\sSOFTWARE\b': 'Crypto.Gitkraken',
    r'(?i)\bIRS\s': 'Taxes.Federal',
    r'(?i)\bINTUIT\s': 'Taxes.Federal',
    # Merrill Lynch transactions
    r'(?i)\bINTEREST:\s': 'Banking.Merrill',
    r'(?i)\bReinvestment\s*Program\s*': 'Banking.Merrill',
    r'(?i)\bDIVIDEND:\s': 'Banking.Merrill',
    r'(?i)\bBANK\sINTEREST:\sML\sBANK\s': 'Banking.Merrill',
    r'(?i)\bPURCHASE:\s': 'Banking.Merrill',
    r'(?i)\bREINVESTMENT\s*SHARE\(S\):': 'Banking.Merrill',
    r'(?i)\bAdvisory\s*Program\s*Fee\s*INV.*': 'Banking.Merrill.Advisory Fee',
    # Credit Card Payments
    r'(?i)\bSYNCHRONY\sBANK\b': 'Credit Cards.Synchrony Bank',
    r'(?i)\bOnline\sBanking\spayment\sto\sCRD\b': 'Credit Cards.Bank of America',
    r'(?i)\bOnline\spayment\sfrom\sCHK\s1391\b': 'Credit Cards.Bank of America',
    r'(?i)\bPayment\s-\sTHANK\sYOU\b': 'Credit Cards.Bank of America',
    r'(?i)\bVisa\sBank\sOf\sAmerica\sBill\sPayment\b': 'Credit Cards.Bank of America',
    r'(?i)\bOnline\sBanking\sTRANSFER\sTO\sCRD\b': 'Credit Cards.Bank of America',
    r'(?i)\bCHASE\sCREDIT\sCRD\b': 'Credit Cards.Chase',
    r'(?i)\bBANK\sOF\sAMERICA\sCREDIT\sCARD\b': 'Credit Cards.Band of America',
    # Transfers
    r'(?i)\bForis\sUSA\sINC\sCF\b': 'Investment.Foris USA',
    r'(?i)\bFID\sBKG\sSVC\sLLC\b': 'Investment.Fidelity',
    r'(?i)\bAgent\sAssisted\stransfer\sfrom\b': 'Investment.Transfer',
    r'(?i)\bMobile\sTransfer\sfrom\sCHK\b': 'Investment.Transfer',    
    r'(?i)\bOnline\sTRANSFER\sTO\sCHK\b': 'Investment.Transfer',
    r'(?i)\bOnline\sBanking\sTRANSFER\sTO\sSAV\b': 'Investment.Transfer.ToSavings',
    r'(?i)\bOnline\sBanking\sTRANSFER\sTO\sINV\b': 'Investment.Transfer.ToInvestments',
    # Travel - General
    r'(?i)\bUNITED.*UNITED\.COM\b': 'Travel.United Airlines',
    r'(?i)\bEXPEDIA\b': 'Travel.Expedia',
    # Travel - Specific Trips
    r'(?i)\bGUNNISON\s*CO\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bIRVING\s*TX\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bEARLY\s*TX\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bSAGUACHE\s*CO\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bSNYDER\s*TX\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bRATON\s*NM\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bDALLAS\s*TX\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bPOST\s*TX\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bCAMPO\s*TX\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bCAMPO\s*CO\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bCHEYENNE\s*WELLCO\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bDUMAS\s*TX\b': 'Travel.ColoradoTripJanuary2025',
    r'(?i)\bLAKE\s*CITY\s*CO\b': 'Travel.ColoradoTripJanuary2025',
    # Unknowns, one-offs (applied last)
    r'(?i)\bID:DIGISTORE\d\d\b': 'Unknown.DIGISTORE',
    r'(?i)\bDIGISTORE\d\d\sINC\.': 'Unknown.DIGISTORE',
    r'(?i)\bID:P3501FEAFA\b': 'Unknown.P3501FEAFA',
    r'(?i)\bID:P334C0CC1F\b': 'Unknown.P334C0CC1F',
    r'(?i)\bRF\s\*BIR\sJV\sLLP\b': 'Unknown.BIR JV LLP',
    r'(?i)\bID:Px*2100\b': 'Unknown.Pxxxxx2100',
    r'(?i)\bPADDLE\.COM\b': 'Unknown.PADDLE-COM',
    r'(?i)\bATGPay\sonline\b': 'Unknown.ATGPay',
    r'(?i)\bWISE\s*US\s*INC\b': 'Unknown.Wise Inc.',
    r'(?i)\bPAYPAL\s*DES:TRANSFER\s*ID:x*\d*\s*\b': 'Unknown.PayPal',
    r'(?i)\bFIT\s*ROUND\s*LAKE-RURAL': 'Unknown',
}
#endregion Category Map
# ---------------------------------------------------------------------------- +
#region category_map_count() function
def category_map_count():
    return len(category_map)
#endregion category_map_count() function

#region map_category() function
def map_category(src_str):
    """Map a transaction description to a budget category."""
    # Run the src_str through the category_map to find a match.
    try:
        for pattern, category in category_map.items():
            if re.search(pattern, str(src_str), re.IGNORECASE):
                return category
        return 'Other'  # Default category if no match is found
    except re.PatternError as e:
        logger.error(p3u.exc_msg(map_category, e))
        logger.error(f'Pattern error: category_map dict: ' 
                     f'{{ \"{e.pattern}\": \"{category}\" }}')
        raise
    except Exception as e:
        logger.error(p3u.exc_msg(map_category, e))
        raise
#endregion map_category() function
