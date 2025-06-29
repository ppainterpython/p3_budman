# ---------------------------------------------------------------------------- +
#region category_mapping.py module
""" Regular Expression techniques to map financial transactions to categories.

    When a workbook is downloaded from a financial institution, the transactions
    typically have a column with a description of the transaction. Herein, a 
    set of regular expressions can be defined to apply to the description and 
    map it to a hierarchical category structure.

"""
#endregion p3_execl_budget.p3_banking_transactions budget_transactions.py module
# ---------------------------------------------------------------------------- +
#region Imports
# python standard library modules and packages
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, Union, List
import re
# third-party modules and packages
import p3logging as p3l, p3_utils as p3u

# local modules and packages.

#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
#logger = logging.getLogger(__name__)
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +
#region BDMTXNCategory class (@dataclass)
@dataclass
class BDMTXNCategory:
    """ BDMTXNCategory is a dataclass that represents a transaction category.
    
    Attributes:
        level1 (str): The first level of the category hierarchy.
        level2 (str): The second level of the category hierarchy.
        level3 (str): The third level of the category hierarchy.
        description (str): A description of the category.
    """
    cat_id: str = field(default="")
    full_cat: str = field(default="")
    level1: str = field(default="")
    level2: str = field(default="")
    level3: str = field(default="")
    payee: str = field(default="")
    description: str = field(default="")
    essential: bool = field(default=False)
    
    def __post_init__(self):
        """Post-initialization to ensure levels are trimmed."""
        self.level1 = self.level1.strip()
        self.level2 = self.level2.strip()
        self.level3 = self.level3.strip()
#endregion BDMTXNCategory
# ---------------------------------------------------------------------------- +
#region check_register_map
# Map a CheckRegister .csv 'Pay-To' field to a Budget Category
# Append 'Check: nnnnn' to level3
# Process a workbook to match 'Checks to Categorize, map in check_register_map,
# replace the desciption with the key value appended with ' - Check: nnnnn' and
# set the Budget_Category.
check_register_map = {
    'Unknown': 'Banking.Checks to Categorize',
    'Nicole Smith': 'Personal Lifestyle.Hair Care.Nicole Smith',
    'Landmark Roofing and Construction': 'New Projects.Home Improvements.Roofing',
    'Tejas Chapter DRT': 'Personal Lifestyle.Professional:Historical Orgs.DRT', #.Tejas Chapter',
    'Maria Oyestas': 'Housing.Maintenance.House Cleaning', #.Maria Oyestas',
    'Passport Services': 'Travel.Passport Services.Check 2883',
    'APQT': 'Medical.Physical Therapy.APQT',
    'Detergent Maria Oyestas': 'Groceries.Detergent Maria Oyestas',
    'Colonel George Moffett Chapter DAR': 'Personal Lifestyle.Professional:Historical Orgs.DAR', #.Colonel George Moffett Chapter',
    'Hannah Painter': 'Misc.Reimbursement.Hannah Painter',
    'Laura Painter': 'Banking.Laura Painter',
    'Lawn Sprinkler': 'Housing.Maintenance.Irrigation System',
    'HVAC Grape Cove Unknown': 'Housing.Maintenance.HVAC',
}
#endregion check_register_map
# ---------------------------------------------------------------------------- +
#region category_map
#region Budget Structure Notes
# category_map : dict[pattern: str, category:str] = {}
# The category_map key is an re:search pattern, that when it matches, the value
# is returned. The pattern is applied to description text and returns a 
# budget category string value.
# This list of patterns will be quite long. 
# In the pattern, (?i) is used to make the pattern case-insensitive. To match
# case, remove that flag.
# TODO: How to use data to train an LLM or ML model to do this?
#
#  Essential Spending Categories:
#  L1: Housing - a place to live, primary residence, mortgage, rent, etc.
#      L2: Mortgage
#      L2: Utilities  - Services to keep the home running.
#          L3: Electricity
#          L3: Water and Waste
#          L3: Natural Gas
#          L3: Internet
#          L3: Phone
#          L3: Home Security
#      L2: Property Taxes
#      L2: Home Owners Association (HOA)
#      L2: Maintenance - Services to keep the home in good repair.
#          L2: HVAC
#          L3: Lawn Care
#          L3: House Cleaning
#          L3: Irrigation System
#  L1: Food
#      L2: Groceries
#      L2: Dining Out
#      L2: Meal Delivery
#  L1: Transportation
#      L2: Auto
#          L3: Gasoline
#          L3: Maintenance
#      L2: Tolls
#      L2: Fees
#          L3: Driver License
#          L3: Registration Fee
#  L1: Medical Expenses
#  L1: Personal Care
#      L2: Hair Care
#      L2: Clothing
#  L1: Insurance
#      L2: Medical Insurance
#      L2: Drug Insurance
#      L2: Dental Insurance
#      L2: Vision Insurance
#      L2: Life Insurance
#      L2: Auto Insurance
#      L2: Home Insurance
#
# Non-Essential Spending Categories: (no-cost options)
#  L1: Personal Lifestyle
#      L2: Storage Unit
#      L2: Dry Cleaning
#      L2: Home Decor
#  L1: Recreation, Entertainment, and Liesure
#  L1: New Projects
#      L2: Home Improvements
#
#endregion Budget Structure Notes
category_map = {
#region Essential Spending Categories
#region L1: Housing - Essential: A roof overhead, a place to live.
    # L1: Housing2 Grape Cove
    r'(?i)\.*OMNT\s*SENT.*CASH\s*APP*JONATHAN.*': 'Housing-2.Maintenance.Lawn Care', #.Jonathan',
    r'(?i)\.*IT\'CLEANING\s*TIME!.*': 'Housing-2.Maintenance.House Cleaning',
    r'(?i)\bReliant\sEnergy\b': 'Housing-2.Utilities.Electricity', #.Reliant Energy',
    r'(?i)\bATMOS\sENERGY\b': 'Housing-2.Utilities.Natural Gas', #.Atmos Energy',
    r'(?i)\bService\sExperts\b': 'Housing-2.Maintenance.HVAC', #.Service Experts',
    r'(?i)\bBrushy\sCreek\sMUD\b': 'Housing-2.Utilities.WaterAndWaste', #.Brushy Creek MUD',
    r'(?i).*BCMUD\s*REC.*': 'Housing-2.Utilities.WaterAndWaste', #.Brushy Creek MUD',
    r'(?i)\bCULLIGAN\b': 'Housing-2.Maintenance.Water Softener', #.Culligan',
    r'(?i)\bCULLINGAN\b': 'Housing-2.Maintenance.Water Softener', #.Culligan',
    r'(?i)\bAT\&T\sU-Verse\b': 'Housing-2.Utilities.Internet', # Connectivity.AT&T U-Verse',
    # L1: Housing - Castle Pines
    #region Utilities
    r'(?i)\bPedernales_Elec\b': 'Housing.Utilities.Electricity', #.Pedernales Electric',
    r'(?i)\bCity\sof\sAustin\b': 'Housing.Utilities.WaterAndWaste', #.City of Austin',
    r'(?i)\bONE\sGAS\b': 'Housing.Utilities.Natural Gas', #.One Gas', # Castle Pines
    r'(?i)\bGoogle\sFIBER\b': 'Housing.Utilities.Internet', # .Google Fiber',
    r'(?i)\bGOOGLE\s\*FIBER\b': 'Housing.Utilities.Internet', # .Google Fiber',
    r'(?i)\bGoogle\s*\*FIBER\b': 'Housing.Utilities.Internet', # .Google Fiber',
    r'(?i)\bAT\&T.*': 'Housing.Utilities.Phone', # .Cellular.AT&T',
    r'(?i)\bATT\b': 'Housing.Utilities.Phone', # .Cellular.AT&T',
    r'(?i)\bVZ\sWIRELESS\sVE': 'Housing.Utilities.Phone', # ',
    r'(?i)\bRING\sBASIC\sPLAN\b': 'Housing.Utilities.Home Security', #.Ring',
    r'(?i)\bRING\s*YEARLY\s*PLAN.*': 'Housing.Utilities.Home Security', #.Ring',
    #endregion Utilities
    #region Maintenance
    r'(?i).*GATOR\s*GARAGE\s*DOORS.*': 'Housing.Maintenance.Home Repair', #.Gator Garage Doors',
    r'(?i)\bFREDERICK\sPEVA\b': 'Housing.Maintenance.Lawn Care', #.Freddie',
    r'(?i)\bTRUGREEN\b': 'Housing.Maintenance.Lawn Care', #.TruGreen',
    r'(?i).*HARBOR\s*FREIGHT.*': 'Housing.Maintenance.Materials', #.Harbor Freight',
    r'(?i)\bTHE\sHOME\sDEPOT\b': 'Housing.Maintenance.Materials', #.Home Depot',
    r"(?i)\bLOWE'?s\b": 'Housing.Maintenance.Materials', #.Lowes',
    r'(?i)\bCASHWAY\sBLDG\sMATERIALS\b': 'Housing.Maintenance.Materials', #.Cashway Building Materials',
    r'(?i)\bFSP\*ABC\sHOME\s&\sCOMMERCIAL': 'Housing.Maintenance.Pest Control', #.ABC Pest Control',
    r'(?i)\bSTRAND\sBROTHERS\sSERVICE\b': 'Housing.Maintenance.HVAC', #.Strand Brothers',
    r'(?i)\bWHITTLESEY\sLANDSCAPE-11\s': 'Housing.Maintenance.Lawn Care', #.Whittlesey Landscape',
    r'(?i)\bTHE\sGRASS\sOUTLET': 'Housing.Maintenance.Lawn Care', #.Grass Outlet',
    #endregion Maintenance
    # Housing General
    r'(?i)\bTRANSFER\s*PAUL\s*B\s*PAINTER\s*LAURA:john\s*hogge\b': 'Housing.Mortgage.Hogge',
    r'(?i)\bTRANSFER\s*PAUL\s*B\s*PAINTER:john\s*hogge\b': 'Housing.Mortgage.Hogge',
    r'(?i)\bavery\W*.*?\branch\W*.*?\bHOA\W*.*?\bdues\b': 'Housing.HomeOwnersAssociation.Avery Ranch',
#endregion L1: Housing - Essential - A roof overhead, a place to live.
#region L1: Transportation - Essential
    r'(?i)\bWILLIAMSON\s*VEHREG.*': 'Transportation.Auto.Fees', #.Registration Fee', #Williamson County Vehicle Registration',
    r'(?i)\bJIFFY\s*LUBE.*': 'Transportation.Auto.Maintenance', #.Jiffy lube',
    r'(?i)\bCALIBER\s*COLLISION.*': 'Transportation.Auto.Body Shop', #.Caliber Collision',
    r'(?i)\bBRAKES\s*PLUS.*': 'Transportation.Auto.Maintenance', #.Brakes Plus',
    r'(?i).*EXPRESS\s*TOLLS.*': 'Transportation.Auto.Tolls', #.Express Tolls',
    r'(?i)\bMINI\s*OF\s*AUSTIN\b': 'Transportation.Auto.Maintenance', #.Mini Cooper',
    r'(?i)\bROUND\s*ROCK\s*HONDA\b': 'Transportation.Auto.Maintenance', #.Honda Ridgeline',
    r'(?i)\bDISCOUNT-TIRE-CO\b': 'Transportation.Auto.Maintenance', #.Tires',
    r"(?i)\bO'REILLY\b": 'Transportation.Auto.Maintenance', #.OReilly',
    r'(?i)\bCHEVRON\b': 'Transportation.Auto.Gasoline', #.Chevron',
    r'(?i)\bSUNOCO\b': 'Transportation.Auto.Gasoline', #.Sunoco',
    r'(?i)\bTEXACO\b': 'Transportation.Auto.Gasoline', #.Texaco',
    r'(?i)\bEXXON\b': 'Transportation.Auto.Gasoline', #.Exxon',
    r'(?i)\bGO\s\bCARWASH\b': 'Transportation.Auto.Carwash', #.Go Carwash',
    r'(?i)\bHCTRA\sEFT\b': 'Transportation.Tolls.HCTRA',
    r'(?i)\bdoxoPLUS\b': 'Transportation.Tolls.DoxoPlus',
    r'(?i)\bRMA\sTOLL\b': 'Transportation.Tolls.RMA',
    r'(?i)\bNTTA.*': 'Transportation.Tolls.NTTA',
    r'(?i)\bTXTAG.*': 'Transportation.Tolls.TxTag',
    r'(?i).*TXDPS\s*DRIVER\s*LICENSE.*': 'Transportation.Auto.Fees', #.Driver License',
    r'(?i)\bWELLS\s*FARGO\s*AUTO': 'Transportation.Auto.Loan', #.Mini Cooper',
    r'(?i)\bSHELL\s*SERVICE\s*': 'Transportation.Auto.Gasoline', #.Shell Service',
    r'(?i)\bCHECKCARD.*CEFCO.*': 'Transportation.Auto.Gasoline', #.CEFCO',
#endregion L1: Transportation: Auto, Tolls, Fees
#region L1: Food - Essential: Groceries, Restaurants, Meal Delivery
    r'(?i).*WHOLEFDS.*': 'Food.Groceries.Whole Foods',
    r'(?i).*DOLLAR\s*TREE.*': 'Food.Groceries.Dollar Tree',
    r'(?i).*WAL-MART.*': 'Food.Groceries.Walmart',
    r'(?i)\bTARGET\b': 'Food.Groceries.H-E-B Pharmacy',
    r'(?i)\bSAMS\s*CLUB\b': 'Food.Groceries.Sams Club',
    r'(?i)\bDOLLAR\sGENERAL\b': 'Food.Groceries.Dollar General',
    r'(?i)\bCOSTCO\sWHSE\b': 'Food.Groceries.CostCo',
    r'(?i)\bH-E-B\b': 'Food.Groceries.H-E-B',
    r'(?i)\bQT\b': 'Food.Groceries.QT',
    r'(?i).*TOTAL\s*WINE\s*AND.*': 'Food.Liquor.Total Wine and More',
    r'(?i)\bTWIN\sLIQUORS\b': 'Food.Liquor.Twin Liquors',
    r'(?i).*KOMEN\sLIQUOR\b': 'Food.Liquor.Komen Liquor',
    r'(?i)\bID:CHEWY\sINC\b': 'Food.Dog Food',
    # Restaurants
    r'(?i).*BELLA\s*SERA.*': 'Food.Restaurants.Bella Sera',
    r'(?i).*CASA\s*GARCIA.*': 'Food.Restaurants.Garcias',
    r'(?i).*LANDRYS.*': 'Food.Restaurants.Landrys',
    r'(?i).*FAVOR\s*SONIC.*DRIVEIN.*': 'Food.Favor.Sonic Drive-In',
    r'(?i).*BURGER\s*KING.*': 'Food.Restaurants.Burger King',
    r'(?i).*GATTILAND\s*ROUND\s*ROCK.*': 'Food.Restaurants.Gattiland',
    r'(?i).*COTTON\s*PATCH\s*CAFE.*': 'Food.Restaurants.Cotton Patch Cafe',
    r'(?i).*CHICK\s*FIL\s*A.*': 'Food.Restaurants.Chick Fil A',
    r'(?i).*POPEYES.*': 'Food.Restaurants.Popeyes',
    r'(?i).*P\.\s*TERRY.*': 'Food.Restaurants.P Terrys',
    r'(?i).*RED\s*ROBIN.*': 'Food.Restaurants.Red Robin',
    r'(?i).*FIVE\s*BELOW.*': 'Food.Restaurants.Five Below',
    r'(?i).*PAPPASITO\'S\s*CANTINA.*': 'Food.Restaurants.Pappasitos Cantina',
    r'(?i).*HUNAN\s*RANCH.*': 'Food.Restaurants.Hunan Ranch',
    r'(?i).*WENDY\'*S\s*.*': 'Food.Restaurants.Wendys',
    r'(?i).*DONUT\s*TACO\s*PALACE.*': 'Food.Restaurants.Donut Taco Palace',
    r'(?i).*PANDA\s*EXPRESS.*': 'Food.Restaurants.Panda Express',
    r'(?i).*RAISING\s*CANES.*': 'Food.Restaurants.Raising Canes',
    r'(?i).*FANN\'S\s*PHILLY\s*GRILL.*': 'Food.Restaurants.Fanns Philly Grill',
    r'(?i).*VILLA\s*FRESH\s*ITALI.*': 'Food.Restaurants.Villa Fresh Italian',
    r'(?i).*THUNDERCLOUD.*': 'Food.Restaurants.Thundercloud Subs',
    r'(?i).*FAVOR\s*HOODYS\s*SUBS.*': 'Food.Favor.Hoodys Subs',
    r'(?i).*BLAZE\s*PIZZA.*': 'Food.Restaurants.Blaze Pizza',
    r'(?i).*SANTIAGO\'*S\s*TEX\s*MEX.*': 'Food.Restaurants.Santiagos Tex Mex',
    r'(?i).*CHEESECAKE\s*AUSTIN.*': 'Food.Restaurants.CheeseCake Austin',
    r'(?i).*SALTGRASS\s*ROUND\s*ROCK.*': 'Food.Restaurants.Saltgrass Round Rock',
    r'(?i).*FWSPRINGCAFE.*': 'Food.Restaurants.FW Spring Cafe',
    r'(?i).*BSWH\s*ROUND\s*ROCK\s*CAFE.*': 'Food.Restaurants.BSW Health Round Rock Cafe',
    r'(?i).*LYNNS\s*TABLE.*': 'Food.Restaurants.Lynns Table',
    r'(?i).*PEPPER\s*AND\s*THE\s*PUG.*': 'Food.Restaurants.Pepper and the Pug',
    r'(?i).*Subway.*': 'Food.Restaurants.Subway',
    r'(?i).*HAT\s*CREEK\s*BURGER.*': 'Food.Restaurants.Hat Creek Burgers',
    r'(?i).*POK-*E-*JO.*': 'Food.Restaurants.Poke Jo\'s',
    r'(?i).*HAYLEYCAKESANDCOOKIES.*': 'Food.Restaurants.Haleys Cakes and Cookies',
    r'(?i).*DAHLIA\s*CAFE.*': 'Food.Restaurants.Dahlia Cafe',
    r'(?i).*MESA\s*ROSA\s*MEXICAN.*': 'Food.Restaurants.Mesa Rosa Mexican',
    r'(?i).*ROUND\s*ROCK\s*DONUTS.*': 'Food.Restaurants.Round Rock Donuts',
    r'(?i).*HOPDODDY.*': 'Food.Restaurants.Hopdoddy',
    r'(?i)\bPANERA\s*BREAD.*': 'Food.Restaurants.Panera Bread',
    r'(?i).*MONUMENT\s*CAFE.*': 'Food.Restaurants.Monument Cafe',
    r'(?i)\bJASON\'S\s*DELI.*': 'Food.Restaurants.Jasons Deli',
    r'(?i).*SHIPLEY\s*DO-NUTS': 'Food.Restaurants.Shipleys Donuts',
    r'(?i).*CHIPOTLE.*': 'Food.Restaurants.Chipotle',
    r'(?i)\bID:STARBUCKS\b': 'Food.Restaurants.Starbucks',
    r'(?i)\bSAVERS\b': 'Food.Restaurants.Savers',
    r"(?i)\b183\sPHIL's\b": 'Food.Restaurants.183 Phils',
    r'(?i)\s\*SMOKEY\sMOS\sBBQ\b': "Food.Restaurants.Smokey Mo's BBQ",
    r'(?i)\bTST\*LA\sMARGARITA\b': 'Food.Restaurants.La Margarita',
    r'(?i)\bSURF\sAND\sTURF\b': 'Food.Restaurants.Surf and Turf',
    r'(?i)\bCASA\sOLE\b': 'Food.Restaurants.Casa Ole',
    r'(?i)\bDAIRY\sQUEEN\b': 'Food.Restaurants.Dairy Queen',
    r'(?i)\bCHICK-FIL-A\b': 'Food.Restaurants.Chick-Fil-A',
    r'(?i)\bMOD\sPIZZA\b': 'Food.Restaurants.Mod Pizza',
    r"(?i)\bMCDONALD'S\b": 'Food.Restaurants.McDonalds',
    r"(?i)\bMANDOLAS\b": 'Food.Restaurants.Mandolas',
    r'(?i)\bTHE\s*LEAGUE\s*KITCHEN\b': 'Food.Restaurants.The League Kitchen',
    r"(?i)\bTONY\sC'S\sCOAL\sFIRED\b": "Food.Restaurants.Tony C's Coal Fired",
    r'(?i)\bTST\*SANTIAGOS\s*TEX\s*MEX\b': 'Food.Restaurants.Santiagos Tex Mex',
    r'(?i)\bPOTBELLY\s': 'Food.Restaurants.PotBelly',
    r'(?i)\bTST\*RUDYS\s*COUNTRY\s*STORE': "Food.Restaurants.Rudy's Country Store",
    r'(?i)\bWHATABURGER\s*': "Food.Restaurants.Whataburger",
    r'(?i).*STARBUCKS.*': "Food.Restaurants.Starbucks",
    r'(?i).*JIMMY\s*JOHNS.*': "Food.Restaurants.Jimmy Johns",
    r'(?i).*MIGHTY\s*FINE\s*BURGERS.*': "Food.Restaurants.Might Fine Burgers",
    r'(?i).*HAT\s*CREEK\s*BURGERS.*': "Food.Restaurants.Hat Creek Burgers",
    r'(?i).*LA\s*MARGARITA.*': "Food.Restaurants.La Margarita",
    r'(?i).*PINTHOUSE\s*PIZZA.*': "Food.Restaurants.Pinthouse Pizza",
    r'(?i).*TACO\s*BELL.*': "Food.Restaurants.Taco Bell",
    r'(?i).*MAMA\s*BETTY.*': "Food.Restaurants.Mama Betty's",
    r'(?i).*OLIVE\s*GARDEN.*': "Food.Restaurants.Olive Garden",
    r'(?i)\bCANTEEN\s*AUSTIN.*': "Food.Restaurants.Canteen Austin",
    r'(?i)\bBSWRR\s*GUEST\s*TRAYS.*': "Food.Restaurants.Hospital",
    r'(?i)\bTOMLINSON\'S\s*FEED.*': "Food.Restaurants.Tomlinson's Feed",
    # Door Dash
    r'(?i)\bID:DOORDASH\b': 'Food.Door Dash',
    r'(?i)\bID:DOORDASHINC\b': 'Food.Door Dash',
    r'(?i)\s\*DOORDASH\b': 'Food.Door Dash',
    r'(?i).*DOORDASH.*': 'Food.Door Dash',
    # Favor
    r'(?i)\bFAVOR\s*TACODELI.*': 'Food.Favor.Taco Deli',
    r'(?i)\bFAVOR\s*TROPICAL\s*SMOOTH.*': 'Food.Favor.Tropical Smoothie',
    r'(?i)\bFAVOR\s*SMOKEYMOS.*': 'Food.Favor.Smokey Mo\'s',
    r'(?i)\bFAVOR\s*PANDA\s*EXPRESS.*': 'Food.Favor.Panda Express',
    r'(?i)\bFAVOR\s*NOODYS.*': 'Food.Favor.Hoodys',
    r'(?i)\bFAVOR\s*AMYS\s*ICE\s*CREAM.*': 'Food.Favor.Amys Ice Cream',
    r'(?i)\bFAVOR\s*PIZZA\s*HUT.*': 'Food.Favor.Amys Ice Cream',
    r'(?i)\bFAVOR\s*MCDONALDS.*': 'Food.Favor.McDonalds',
    r'(?i)\bFAVOR\s*SLAPBOX\s*PIZZ.*': 'Food.Favor.Slapbox Pizza',
#endregion L1: Food: Groceries, Restaurants, Meal Delivery
#region L1: Insurance - Essential
    r'(?i)\bPRINCIPAL-CCA\b': 'Insurance.Life Insurance.Principal Life Insurance',
    r'(?i)\bHP\s*\bDES:INS\sPREM\b': 'Insurance.Medical Insurance.Cobra Medical',
    r'(?i)\bSWHP\s*\bDES:HEALTH\s*INS\s': 'Insurance.Medical Insurance.Cobra Medical',
    r'(?i)\bState\s\bFARM\b': 'Insurance.Auto and Home.State Farm',
    r'(?i)\bAAA\s*TX.*': 'Insurance.Auto Insurance.AAA Texas',
    r'(?i)\bTexas\s*Law\b': 'Insurance.Personal Liability.Texas Law',
#endregion L1: Insurance
#region L1: Medical - Essential
    r'(?i).*FLEXBUDDY.*': 'Medical.Supplies.FlexBuddy',
    r'(?i).*ZENSAH\s*COMPRESSIO.*': 'Medical.Supplies.Zensah Compression',
    r'(?i).*THERAICERX.*': 'Medical.Supplies.TheraIceRx',
    r'(?i).*CARENOW.*': 'Medical.CareNow',
    r'(?i)\bGEORGETOWN\sOB-GYN\b': 'Medical.Bio-T',
    r'(?i)\bQDI\*QUEST\sDIAGNOSTICS\b': 'Medical.Labs',
    r'(?i)\bHAROLD\sF\sADELMAN\sMD\b': 'Medical.Adelman',
    r'(?i)\bBSWHealth.*\b': 'Medical.BSW Health',
    r'(?i)\bJOHN\sF\sLANN\sDDS\b': 'Medical.Dental.Lann',
    r'(?i)\bCVS/PHARM\b': 'Medical.Pharmacy.CVS',
    r'(?i)\bCAREMARK\sMAIL\b': 'Medical.Pharmacy.CVS',
    r'(?i)\bWWW\.CAREMARK\.COM\b': 'Medical.Pharmacy.CVS',
    r'(?i)\bCVS.*PHARMACY\b': 'Medical.Pharmacy.CVS',
    r'(?i)\bMINUTECLINIC\b': 'Medical.Pharmacy.CVS Minute Clinic',
    r'(?i)\bNORTHWEST\s*HILLS\s*EYE\b': 'Medical.Eye Doctor.Northwest Hills Eye Care',
    r'(?i)\bWWW\.NWHILLSEYECARE\.COM.*': 'Medical.Eye Doctor.Northwest Hills Eye Care',
    r'(?i)\bLONE\s*STAR\s*ONCOLOGY\b': 'Medical.Oncology',
    r'(?i)\bBACKBONE\s*WELLNESS.*': 'Medical.Chiropractor',
    r'(?i)\bQuest\s*Diagnostic\s': 'Medical.Labs',
    r'(?i)\bLABORATORY\s*CORPORATION\s': 'Medical.Labs',
    r'(?i).*YSA\s*REIMB\b': 'Medical.Reimbursement',
    r'(?i)\bASSOCIATES\s*OF\s*AUDIOLOGY\b': 'Medical.Audiology',
    r'(?i)\bTEXAS\s*SPINE\s*AND\s*SPORTS\b': 'Medical.Physical Therapy',
    r'(?i)\bTHERABODY\b': 'Medical.TheraBody',
    r'(?i).*DERM\s*PARTNERS.*': 'Medical.Dermatology',
    r'(?i)\bWWW\.BODYSPEC\.COM\b': 'Medical.Labs.BodySpec',
    r'(?i).*TEXAN\s*EYE.*': 'Medical.Eye Doctor.Texan Eye',
    r'(?i)\bCENTRAL\s*TEXAS\s*RHEUMATO.*': 'Medical.Rheumatology.Olga',
    r'(?i).*TOUCHSTONE\s*IMAGING.*': 'Medical.Radiology.Touchstone Imaging',
    r'(?i).*AUSTIN\s*RADIOLOGICAL.*': 'Medical.Radiology.Austin Radiological',
    r'(?i)\bGREAT\sOAKS\sANIMAL\b': 'Medical.Veterinary',
#endregion L1: Medical
#endregion Essential Spending Categories
#region Non-Essential Spending Categories
#region Personal Lifestyle - Non-Essential
    #region Donations
    r'(?i).*WATERSTONE.*': 'Personal Lifestyle.Donation.Charity', # .GCR',
    r'(?i)\bPioneers\s*USA.*': 'Personal Lifestyle.Donation.Charity', # .Pioneers',
    r'(?i)\bCAMPUS\s\bCRUSADE\b': 'Personal Lifestyle.Donation.Charity', # .Campus Crusade',
    r'(?i)\bTUNNELTOTOWERS\b': 'Personal Lifestyle.Donation.Charity', # .Tunnel to Towers',
    r'(?i)\bFOCUS\sON\sTHE\sFAMILY\b': 'Personal Lifestyle.Donation.Charity', # .Focus on the Family',
    r'(?i)\bPioneers\sBlueChe\b': 'Personal Lifestyle.Donation.Charity', # .Pioneers',
    r'(?i)\bST\sJUDE\b': 'Personal Lifestyle.Donation.Charity',  #.St Jude',
    r'(?i)\bWorld\s*Vision\s*Inc\b': 'Personal Lifestyle.Donation.Charity', # .World Vision',
    r'(?i)\bDAYSTAR\s*TELEVISION': 'Personal Lifestyle.Donation.Charity', # .DayStar',
    r'(?i)\bI*D*:*GOFUNDME\sJOHN\sW.*': 'Personal Lifestyle.Donation', # .GoFundMe.John Wick',
    r'(?i)\bWINRED\*\s*NRSC\b': 'Personal Lifestyle.Donation.Politics', # .Republican Party',
    r'(?i)\bWINRED\*\s*': 'Personal Lifestyle.Donation.Politics', # .Republican Party',
    #endregion Donations
    #region Fitness and Wellbeing
    r'(?i)\bID:23ANDME\s*INC\b': 'Personal Lifestyle.Fitness and Wellbeing.23andMe',
    r'(?i)\b23ANDME.*': 'Personal Lifestyle.Fitness and Wellbeing.23AndMe',
    r'(?i)\bLIVEWELLO.*': 'Personal Lifestyle.Fitness and Wellbeing.LiveWello',
    r'(?i)\bNUTRISENSE.*': 'Personal Lifestyle.Fitness and Wellbeing.NutriSense',
    r'(?i)\bHand\s*Stone\s*Spa.*': 'Personal Lifestyle.Fitness and Wellbeing.Massage',
    r'(?i)\bDicks\s*Sporting\s*Goods.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment',
    r'(?i)\bV\s*SHRED.*': 'Personal Lifestyle.Fitness and Wellbeing.Supplements', #.V Shred',
    r'(?i)\bPELOTON.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', #.Peloton',
    r'(?i).*SWIMOUTLET.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', # swimming
    r'(?i).*UNDERWATER\s*AUDIO.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', #Swimming.Underwater Audio',
    r'(?i)\bFINLEYS\sAVERY\sRANCH\b': 'Personal Lifestyle.Hair Care.Finleys Barbershop Avery Ranch',
    r'(?i)\bCATHY\s\bDUNFORD\b': 'Personal Lifestyle.Fitness and Wellbeing.Life Coach', #.Cathy Dunford',
    r'(?i)\bSNICOLA\s\bMCKERLIE\b': 'Personal Lifestyle.Fitness and Wellbeing.Personal Trainer', #.Nicola McKerlie',
    r'(?i)\bNEW\s*TECH\s*TENNIS': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', #Tennis.Equipment',
    r'(?i)\bPLAYITAGAINSPORTS.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', #Tennis.Equipment',
    r'(?i)\bSPINFIRE.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', #Tennis.Equipment',
    r'(?i)\bTHE\s*TENNIS\s*SHO.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', #Tennis.Equipment',
    r'(?i).*ATHLETA.*': 'Personal Lifestyle.Fitness and Wellbeing.Athleta',
    r'(?i).*FLEET\s*FEET.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', #.Fleet Feet',
    r'(?i)\bTHE\s*PEDDLER\s*BICYCLE.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', #Cycling.The Peddler Bicycle Shop',
    r'(?i)\bTrek\s*Bicycle\s*Parmer.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', #Cycling.Trek Bicycle Shop',
    r'(?i).*ELLIPTIGO.*': 'Personal Lifestyle.Fitness and Wellbeing.Equipment', #Cycling.Elliptigo',
    #endregion Fitness and Wellbeing
    # Hobby
    r'(?i)\bPRECISION\s*CAMERA.*': 'Personal Lifestyle.Hobby.Photography', #.Precision Camera',
    r'(?i)\bJERRY\'S\s*ARTARAMA.*': 'Hobby.Artwork.Jerrys Artarama',
    r'(?i)\bID:INSTITUTEEL\b': 'Personal Lifestyle.Professional:Historical Orgs.IEEE',
    # Dry Cleaning
    r'(?i)\bJack\sBrown\sCleaners': 'Personal Lifestyle.Dry Cleaning', #.Jack Brown Cleaners',
    # Storage Unit
    r'(?i)\bRIGHTSPACE\sSTORAGE\b': 'Personal Lifestyle.Storage Unit', #.RightSpace Storage',
    # Home Decor
    r'(?i)\bFRAMEITEASY\.COM*': 'Personal Lifestyle.Home Decor', #.Frame It Easy',
    # Pets
    r'(?i).*PETSMART.*': 'Pets.Misc.PetSmart',
    r'(?i)\bPETSUITES\sGREAT\sOAKS\b': 'Pets.Boarding',
    r'(?i)\bMUD\s*PUPPIES\b': 'Pets.Grooming',
    #region Online Services
    r'(?i).*EXPRESSVPN\.COM.*': 'Personal Lifestyle.Online Subscription.Application', #.Express VPN',
    r'(?i).*MUSESCORE.*': 'Personal Lifestyle.Online Subscription.Content', #.Sheet Music',
    r'(?i).*CEREBRUM\s*IQ.*': 'Personal Lifestyle.Online Subscription.Application', #.Creberum IQ',
    r'(?i).*MINDJET\s*COREL.*': 'Personal Lifestyle.Online Subscription.Software', #.MindJet',
    r'(?i).*PHOTO\s*ERASER\s*APP.*': 'Personal Lifestyle.Online Subscription.Software', #.Photo Eraser',
    r'(?i).*OPENAI.*': 'Personal Lifestyle.Online Subscription.Content', #.OpenAI',
    r'(?i)\bA\s*MEDIUM\s*CORPORATION.*': 'Personal Lifestyle.Online Subscription.Content', #.Medium',
    r'(?i)\bFS.*stardock.*': 'Personal Lifestyle.Online Subscription.Software', #.Stardock',
    r'(?i)\bID:ANCESTO*RYCOM\b': 'Personal Lifestyle.Online Subscription.Content', #.Ancestry-com',
    r'(?i).*TEAMVIEWER.*': 'Personal Lifestyle.Online Subscription.Application', #.TeamViewer',
    r'(?i)\bID:ADOBE\sINC\b': 'Personal Lifestyle.Online Subscription.Software', #.Adobe',
    r'(?i)\bID:ANGIES\sLIST\b': 'Personal Lifestyle.Online Subscription.Application', #.Angies List',
    r'(?i)\bID:GITHUB\sINC\b': 'Personal Lifestyle.Online Subscription.Application', #.GitHub',
    r'(?i)\bGITKRAKEN\sSOFTWARE\b': 'Personal Lifestyle.Online Subscription.Application', #.Gitkraken Crypto',
    r'(?i)\bID:PATREON\s*MEMBER\b': 'Personal Lifestyle.Online Subscription.Patreon',
    r'(?i)\bID:DROPBOX\b': 'Personal Lifestyle.Online Subscription.Storage', #.DropBox',
    r'(?i)\bwikimedia\b': 'Personal Lifestyle.Online Subscription.Content', #.WikiPedia',
    r'(?i)\bPAYPAL\b.*ID:CLEVERBRIDG': 'Personal Lifestyle.Online Subscription.Software',
    r'(?i)\bCHECKCARD\b.*APPLE\sCOM\sBILL': 'Personal Lifestyle.Online Subscription.Storage', #.Apple',
    r'(?i)\bDREAMSTIME\.COM.*': 'Personal Lifestyle.Online Subscription.Application', #.Dreamstime',
    r'(?i)\bLEGALNATURE\b': 'Personal Lifestyle.Online Subscription.Application', #.Legal Nature',
    r'(?i).*Classmates\.com.*': 'Personal Lifestyle.Online Subscription.Application', #.Classmates',
    r'(?i).*POSTMAN\s*BASIC\s*.*': 'Personal Lifestyle.Online Subscription.Application', #.Postman',
    r'(?i).*MCONVERTER\.EU.*': 'Personal Lifestyle.Online Subscription.Software', #.MConverter',
    r'(?i)\bSP\s*ROAD\s*ID.*': 'Personal Lifestyle.Online Subscription.Application', #.Road ID',
    r'(?i).*CODE\s*MAGAZINE.*': 'Personal Lifestyle.Online Subscription.Content', #.CODE Magazine',
    #endregion Online Services
#endregion Personal Lifestyle
#region Entertainment - Streaming, Concerts, Theater
    r'(?i)\bMUSEUM\s*OF\s*ILLUSION.*': 'Entertainment.Museums.Museum of Illusion',
    r'(?i)\bMOI\s*AUSTIN.*': 'Entertainment.Museums.Museum of Illusion',
    r'(?i)\bBALLET\s*AUSTIN.*': 'Entertainment.Theater.Austin Ballet',
    r'(?i)\bGoogle\s*Play\s*Books.*': 'Entertainment.Streaming.Google Play Books',
    r'(?i)\bSXM\*SIRIUSXM\.COM/ACCT\b': 'Entertainment.Streaming.SiriusXM',
    r'(?i)\bCINEMARK\b': 'Entertainment.Theater.Cinemark',
    r'(?i)\bAudible\*.*\b': 'Entertainment.Streaming.Audible',
    r'(?i)\bSLING\.COM\b': 'Entertainment.Streaming.SlingTV',
    r'(?i)\bID:HULU\b': 'Entertainment.Streaming.Hulu',
    r'(?i)\bPrime\s\bVideo\b': 'Entertainment.Streaming.Amazon Prime Video',
    r'(?i)\bTHIRTEEN\b': 'Entertainment.Streaming.Thirteen',
    r'(?i)\bID:NETFLIX\.COM\b': 'Entertainment.Streaming.Netflix',
    r'(?i)\bSUNDANCE\s*NOW.*': 'Entertainment.Streaming.Sundance Now',
    r'(?i)\bKindle\b.*Svcs.*': 'Entertainment.Streaming.Kindle',
    r'(?i)\bGOOGLE.*YouTubePremium.*': 'Entertainment.Streaming.YouTube Premium',
    r'(?i)\bDisney.*Plus.*': 'Entertainment.Streaming.Disney Plus',
    r'(?i)\bSPOTIFY\b': 'Entertainment.Streaming.Spotify',
    r'(?i).*DIRECTV?.*STREAM\b': 'Entertainment.Streaming.DirectTV Stream',
    r'(?i).*DIRECTV\s*SERVICE.*': 'Entertainment.Streaming.DirectTV Service',
    r'(?i).*BRIT\s*FLOYD.*': 'Entertainment.Concerts.Brit Floyd',
    r'(?i)\bWWW\.MUBI\.COM\b': 'Entertainment.Streaming.MUBI TV',
    r'(?i)\bGO\s*TICKETS.*': 'Entertainment.Concerts.Go Tickets',
    r'(?i)\bSTUBHUB.*': 'Entertainment.Concerts.StubHub',
    r'(?i)\bMOODY\s*CENTER.*': 'Entertainment.Concerts.Moody Center',
    r'(?i).*TYPHOON\s*TEXAS.*': 'Entertainment.Typhoon Texas',
    r'(?i)\bTM.*TICKETMASTER.*': 'Entertainment.Concerts.Ticketmaster',
    r'(?i)\bTM.*BARRY\s*MANILOW.*': 'Entertainment.Concerts.Barry Manilow',
    r'(?i)\bTM.*EAGLES\s*LIVE\s*AT\s*SPH.*': 'Entertainment.Concerts.The Eagles Live at the Sphere',
    r'(?i).*INDIGO\s*PLAY': 'Entertainment.Misc.Indigo Play',
    r'(?i)\bTM.*EAGLES\s*LIVE\s*AT\s*SPH.*': 'Entertainment.Concerts.The Eagles Live at the Sphere',
    r'(?i)\bTM.*EAGLES.*': 'Entertainment.Concerts.The Eagles',
    r'(?i)\bTM.*KACEY\s*MUSGRAVES.*': 'Entertainment.Concerts.The Eagles',
#endregion Entertainment - Streaming, Concerts, Theater
#region Shopping - Amazon, Apple, Clothing, etc.
    r'(?i).*APOLLA\s*PERFORM.*': 'Clothing.Apparel.Apolla Performance',
    r'(?i).*DILLARDS.*': 'Clothing.Apparel.Dillards',
    r'(?i).*ALPAKA\s*GEAR.*': 'Clothing.Apparel.Alpaka Gear',
    r'(?i).*KURU\s*FOOTWEAR.*': 'Clothing.Shoes.Kuru Footwear',
    r'(?i).*VANS.*': 'Clothing.Shoes.Vans',
    r'(?i).*LEVI\'S\s*OUTLET.*': 'Clothing.Apparel.Levi\'s Outlet',
    r'(?i)\bJ\.\s*CREW\s*FACTOR\b': 'Clothing.Apparel.J Crew',
    r'(?i)\bSP\s*PEAKDESIGN\b': 'Clothing.Apparel.Peak Design',
    r'(?i)\bCrocs.*': 'Clothing.Shoes.Crocs',
    r'(?i).*THE\s*HAT\s*PEOPLE.*': 'Clothing.Hats.The Hat People',
    r'(?i).*DULUTH\s*TRADING': 'Clothing.Apparel.Duluth Trading Company',
    r'(?i).*DUCKFEET\s*USA.*': 'Clothing.Shoes.Duckfeet USA',
    r'(?i).*KOHLS\.COM.*': 'Clothing.Apparel.Kohls',
    r'(?i).*COMFORT\s*SHOE\s*STORES.*': 'Clothing.Shoes.Comfort Shoe Stores',
    r'(?i)\bID:RUNNINGWARE\b': 'Clothing.Shoes.Running Warehouse',
    r'(?i)\bMARDEL\b': 'Shopping.Misc.Mardel',
    r'(?i)\bBUC-EE\'S\b': 'Shopping.Misc.Buc-ees',
    r'(?i).*SADDLEBACK.*': 'Shopping.SaddleBack Leather',
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
    r'(?i)\bAMAZON\s': 'Shopping.Amazon',
    r'(?i)\bAMZN\s*Mktp': 'Shopping.Amazon Marketplace',
    r'(?i).*AMAZON.*': 'Shopping.Amazon',
    r'(?i)\b.*APPLE\.COM.*\b': 'Shopping.Apple',
    r'(?i)\bCIRCLE\sK\b': 'Shopping.Circle K',
    r'(?i)\b7-ELEVEN\b': 'Shopping.7-Eleven',
    r'(?i)\bMICHAELS\sSTORES\b': 'Shopping.Michaels',
    r'(?i)\bWALGREENS\s*(STORE)*\b': 'Shopping.Walgreens',
    r'(?i)\bPAYPAL\s*(STORE)*\b': 'Shopping.Walgreens',
    r'(?i)\bPAYPAL\s': 'Shopping.PayPal',
    r'(?i)\bSMART\sSTOP': 'Shopping.Misc',
    r'(?i)\bSPEEDY\sSTOP': 'Shopping.Misc',
    r'(?i).*COSTCO.*': 'Shopping.Costco',
    r'(?i)\bJames\s*Avery.*': 'Shopping.James Avery',
    r'(?i)\bFEDEX.*': 'Shopping.Shipping.FedEx',
    r'(?i)\bPALMETTO\s*STATE\s*ARMORY.*': 'Shopping.Firearms.Palmetto State Armory',
    r'(?i)\bBEST\s*BUY.*': 'Shopping.Misc.Best Buy',
    r'(?i)\bSAND\s*CLOUD\s*TOWELS.*': 'Shopping.Misc.Sand Cloud Towels',
    r'(?i)\bSHELL\s*OIL\s*': 'Shopping.ConvenienceStore.Shell Oil',
    r'(?i).*CPAYNESBOOK': 'Shopping.Misc.Charles Paynes Book',
    r'(?i)\bREI\.COM.*': 'Shopping.Misc.REI',
    r'(?i)\bREI.*': 'Shopping.Misc.REI',
    r'(?i).*POST\s*OFFICE\s*AT\s*RIGHTSPA.*': 'Shopping.Shipping.RightSpace',
    r'(?i).*WHOLE\s*EARTH\s*PROVISION*': 'Shopping.Misc.Whole Earth Provision',
#endregion Shopping - Amazon, Apple, etc.
#region Shopping - Misc. for review.
    r'(?i).*THP\s*NEA\s*ONLINE.*': 'Shopping.Misc.THP NEA Online',
    r'(?i).*TST\*STILES\s*SWITCH.*': 'Shopping.Misc.Stiles Switch',
    r'(?i).*ORNAMENT\s*SHOP.*': 'Shopping.Misc.Ornament Shop',
    r'(?i).*RUSSELL\s*CELLULAR.*': 'Shopping.Misc.Russell Cellular',
    r'(?i).*TST\*AUSTINS.*': 'Shopping.Misc.TST Austins',
    r'(?i).*Redbud\s*Elementar.*': 'Shopping.Misc.Redbud Elementary School',
    r'(?i).*PEOPLECERT.*': 'Shopping.Misc.PeopleCert',
    r'(?i).*PARTY\s*CITY.*': 'Shopping.Misc.Party City',
    r'(?i).*AMERICAN\s*EXPRESS.*': 'Shopping.Misc.American Express',
    r'(?i).*Staples.*': 'Shopping.Misc.Staples',
    r'(?i).*54TH\s*STREET.*': 'Shopping.Misc.54TH Street',
    r'(?i).*CEFCO.*': 'Shopping.Convenience Stores.Cefco',
    r'(?i).*GODAVARI\s*AUSTIN.*': 'Shopping.Misc.Godavari Austin',
    r'(?i).*GATEWAY\s*EXPRES.*': 'Shopping.Misc.Gateway Express',
    r'(?i).*KLIPSTA.*': 'Shopping.Misc.Klipsta',
    r'(?i).*PLUM\s*SPA.*': 'Shopping.Misc.Plum Spa',
    r'(?i).*CANTEEN\s*10.*': 'Shopping.Misc.Canteen 10',
    r'(?i).*SHOP\.TSHELLZ\.COM.*': 'Shopping.Misc.Shop TSHELLZ Com',
    r'(?i).*AUSTIN-BERGSTROM.*': 'Shopping.Misc.Austin Bergstrom',
    r'(?i).*TEXAS\s*GIFT.*': 'Shopping.Misc.Texas Gift Outlet',
    r'(?i).*STROLEE\s*CARTS.*': 'Shopping.Misc.Strolee Carts',
    r'(?i)\bSP\s*PAPERLIKE.*': 'Shopping.Misc.PAPERLIKE',
    r'(?i).*OOFOS.*': 'Shopping.Misc.OOFOS',
    r'(?i).*TERRA\s*TOYS.*': 'Shopping.Misc.Terra Toys',
    r'(?i).*THE\s*UPS\s*STORE.*': 'Shopping.Misc.The UPS Store',
    r'(?i).*SUNBUSTERS\s*WINDOW\s*TINT.*': 'Shopping.Misc.Sunbusters Window Tint',
    r'(?i)\bGWCTX.*': 'Shopping.Misc.GWCTX',
    r'(?i)\bL*S*\s*SOUTHERN\s*LEISURE.*': 'Shopping.Misc.Southern Leisure',
    r'(?i)\bCEDAR\s*PARK\s*JEWELRY.*': 'Shopping.Jewelry.Cedar Park Jewelry',
    r'(?i)\bCarts\s*Chairs\s*SmarteCarte.*': 'Shopping.Misc.SmarteCarte',
    r'(?i)\bOFFERINGTREE.*': 'Shopping.Misc.OfferingTree',
    r'(?i)\bMOMENT.*': 'Shopping.Misc.Moment',
    r'(?i)\bS*P*\s*SHIFTCAM.*': 'Shopping.Misc.ShiftCam',
    r'(?i)\bSIX\s*MILLION\s*VOICES.*': 'Shopping.Misc.Six Million Voices',
    r'(?i)\bSP\s*SANDMARC.*': 'Shopping.Misc.SandMarc',
    r'(?i)\bSP\s*PEN\s*TIPS.*': 'Shopping.Misc.Groningen',
    r'(?i)\bRMCF.*': 'Shopping.Misc.RMCF',
    r'(?i)\bS*P*\s*ONDO\s*INC.*': 'Shopping.Misc.Ondo',
    r'(?i)\bS*P*\s*CADENCE*': 'Shopping.Misc.Ondo',
#endregion Shopping - Misc. for review.
#region New Projects - Non-Essential
    r'(?i).*TDS\s*LANDFILL.*': 'New Projects.Selling Grape Cove.Expenses',  #.TDS Landfill',
    r'(?i)\.*SOLEIL\s*FLOORS.*': 'New Projects.Home Improvements.Flooring', #Soleil Floors',
#endregion New Projects
#region Work-related Expenses
    r'(?i)\bRHEINWERK\/SAP\s*PRESS.*\b': 'Work-related.Training.SAP',
    r'(?i)\b.*ZOOMCOMM.*\b': 'Personal Lifestyle.Online Subscription.Zoom',
    r'(?i)\bVISUALMIND\s*APP\b': 'Work-related.VisualMind',
    r'(?i)\bEXECUTIVE\sCAREER\sUPGRA\b': 'Work-related.ECU Recruiting',
    r'(?i)\bOTTER\.AI\b': 'Work-related.OTTER-AI',
    r'(?i)\bID:LINKEDIN\b': 'Work-related.Linked In',
    r'(?i)\bID:LINKEDIN\b': 'Work-related.Linked In',
    r'(?i)\bLinkedIn.*': 'Work-related.Linked In',
    r'(?i)esferas\.io': 'Work-related.ECU Recruiting',
    r'(?i)JetBrains': 'Work-related.Software.JetBrains',
    r'(?i)Varsity\s*TUTORS': 'Work-related.Training.Varsity Tutors',
#endregion Work-related Expenses
#region Income
    r'(?i)\bInterest\sEarned\b': 'Income.Interest',
    r'(?i)\bGerson\sLehrman\sG\b': 'Income.Consulting.GL Group',
    r'(?i)\bHP\sINC*?\bPAYROLL\b': 'Income.HP Inc',
    r'(?i)\bHP\sINC\.\s*\bDES:PAYROLL\b': 'Income.HP Inc',
    r'(?i)\bTWC-BENEFITS\b': 'Income.TWC.',
    r'(?i)\bBank\s*of\s*America.*CASHREWARD': 'Income.Bank Reward',
    r'(?i)\bZelle\s*payment\s*from\s*JOHN\s*PAINTER': 'Income.Inheritance.John Painter',
#endregion Income
#region Banking, Finance and Taxes 
    r'(?i)\bOVERDRAFT\s*PROTECTION.*': 'Banking.Overdraft Protection',
    r'(?i)\bPMNT\s*SENT.*APPLE\s*CASH\s*SENT\s*MONEY.*': 'Banking.Apple Cash',
    r'(?i)\bBANK\s*-\s*TRANSACTION\s*FEE.*': 'Banking.Transaction Fee',
    r'(?i)\bBANK\s*OF\s*AMERICA.*': 'Banking.Crypto',
    r'(?i)\bBOFA\s*FIN\s*CTR.*': 'Banking.Transaction',
    r'(?i)\bBKOFAMERICA.*': 'Banking.Transaction',
    r'(?i)\bTNB\s*FINANCIAL.*': 'Banking.TNB Financial',
    r'(?i)\bAdjustment\/Correction.*': 'Banking.Adjustment',
    r'(?i)\bOnline\s*(Banking)*\s*payment.*from\s*SAV.*': 'Banking.Payment.From Savings 0196',
    r'(?i)\bOnline\s*Banking\s*transfer.*from\s*SAV.*': 'Banking.Transfer.From Savings 0196',
    r'(?i)\bPMNT\s*SENT.*CASH\s*APP.*ROBIN\s*PAINTER.*': 'Banking.Transfer.Robin Painter',
    r'(?i)\bOnline\s*Banking\s*Transfer.*Painter,\s*ROBIN.*': 'Banking.Transfer.Robin Painter',
    r'(?i)\bOnline\s*Banking\s*Transfer.*Painter,\s*JUSTIN.*': 'Banking.Transfer.Justin Painter',
    r'(?i)\bPreferred\s*Rewards.*\b': 'Banking.Preferred Rewards',
    r'(?i)\bLATE\sFEE\sFOR\sPAYMENT\sDUE\b': 'Banking.Late Fee',
    r'(?i)\bINTEREST\sCHARGED\sON\sPURCHASES\b': 'Banking.Interest',
    r'(?i)\bFRAUD\sDISPUTE\b': 'Banking.Fraud Dispute',
    r'(?i)\bGB\sREVERS(AL|ED)\b': 'Banking.Fraud Dispute',
    r'(?i)\bFOREIGN\sTRANSACTION\sFEE\b': 'Banking.Foreign Transaction Fee',
    r'(?i)\bExperian\*\sCredit\sReport\b': 'Finance.Experian',
    r'(?i)\bBKOFAMERICA\sATM.*\bWITHDRWL\b': 'Banking.ATM',
    r'(?i)\bBKOFAMERICA\sMOBILE.*\bDEPOSIT\b': 'Banking.Mobile Deposit',
    r'(?i)\bMobile\s*transfer\s*to\s*CHK.*': 'Banking.Transfer.To Checking',
    r'(?i)\bWIRE\s*TYPE:WIRE\s*OUT.*': 'Crypto.Transfer.To CryptoCom',
    # Taxes
    r'(?i)\bIRS\s': 'Taxes.Federal',
    r'(?i)\bINTUIT\s': 'Taxes.Federal',
    r'(?i)\bWILLIAMSON\s*COUNT\s*DES:EPAYMENT\b': 'Housing.Property Taxes.Williamson County',  
    r'(?i)\bPMT\*WILCO\sTAX\b': 'Housing.Property Taxes.Williamson County',
    r'(?i)\.*WILLIAMSON\s*COUNT.*': 'Housing.Property Taxes.Williamson County',

#endregion Banking, Finance and Taxes 
#region Merrill Lynch transactions
    r'(?i)\bINTEREST:\s': 'Banking.Merrill',
    r'(?i)\bReinvestment\s*Program\s*': 'Banking.Merrill',
    r'(?i).*DIVIDEND:\s.*': 'Banking.Merrill',
    r'(?i)\bSALE:\s': 'Banking.Merrill',
    r'(?i)\bRETURN\s*OF\s*CAPITAL:\s': 'Banking.Merrill',
    r'(?i)\bBANK\sINTEREST:\sML\sBANK\s': 'Banking.Merrill',
    r'(?i)\bPURCHASE:\s': 'Banking.Merrill',
    r'(?i)\bREINVESTMENT\s*SHARE\(S\):': 'Banking.Merrill',
    r'(?i)\bAdvisory\s*Program\s*Fee\s*INV.*': 'Banking.Merrill.Advisory Fee',
#endregion Merrill Lynch transactions
#region Credit Card Payments
    r'(?i)\bSYNCHRONY\sBANK\b': 'Credit Cards.Synchrony Bank',
    r'(?i)\bOnline\sBanking\spayment\sto\sCRD\b': 'Credit Cards.Bank of America',
    r'(?i)\bOnline\spayment\sfrom\sCHK\s1391\b': 'Credit Cards.Bank of America',
    r'(?i)\bPayment\s-\sTHANK\sYOU\b': 'Credit Cards.Bank of America',
    r'(?i)\bVisa\sBank\sOf\sAmerica\sBill\sPayment\b': 'Credit Cards.Bank of America',
    r'(?i)\bOnline\sBanking\sTRANSFER\sTO\sCRD\b': 'Credit Cards.Bank of America',
    r'(?i)\bCHASE\sCREDIT\sCRD\b': 'Credit Cards.Chase',
    r'(?i)\bBANK\sOF\sAMERICA\sCREDIT\sCARD\b': 'Credit Cards.Band of America',
#endregion Credit Card Payments
#region Transfers
    r'(?i)\bForis\sUSA\sINC\sCF\b': 'Investment.Foris USA',
    r'(?i)\bFID\sBKG\sSVC\sLLC\b': 'Investment.Fidelity',
    r'(?i)\bWIRE\s*TYPE:BOOK.*': 'Investment.Fidelity',
    r'(?i)\bWIRE\s*TYPE:WIRE\s*IN.*': 'Investment.Fidelity',
    r'(?i)\bAgent\sAssisted\stransfer\sfrom\b': 'Investment.Transfer',
    r'(?i)\bMobile\sTransfer\sfrom\sCHK\b': 'Investment.Transfer',    
    r'(?i)\bOnline\sTRANSFER\sTO\sCHK\b': 'Investment.Transfer',
    r'(?i)\bOnline\sBanking\sTRANSFER\sTO\sSAV\b': 'Investment.Transfer.ToSavings',
    r'(?i)\bOnline\sBanking\sTRANSFER\sTO\sINV\b': 'Investment.Transfer.ToInvestments',
#endregion Transfers
#region Travel - General
    r'(?i)\bCLEAR.*clearme\.com.*': 'Travel.Clear',
    r'(?i).*AUSTIN\s*AIRPORT.*': 'Travel.Food.Austin Airport',
    r'(?i).*UNITED\s*CLUB.*': 'Travel.Food.United Club',
    r'(?i).*LAZ\s*PARKING.*': 'Travel.Parking',
    r'(?i)\bUNITED.*UNITED\.COM\b': 'Travel.United Airlines',
    r'(?i)\bUNITED.*': 'Travel.United Airlines',
    r'(?i).*ALASKA\s*AIR.*': 'Travel.Alaska Airlines',
    r'(?i)\bEXPEDIA\b': 'Travel.Expedia',
    r'(?i).*WANDRD.*': 'Travel.Luggage.Wandrd',
    r'(?i)\bALLIANZ\s*EVENT\s*INS.*': 'Travel.Trip Insurance',
    r'(?i)\bLYFT.*RIDE.*': 'Travel.Transportation.Lyft',
#endregion Travel - General
#region Travel - Specific Trips
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
    r'(?i)\bBARYSHNIKOV\s*ARTS\s*CENTER\b': 'Travel.NewYorkMarch2024',
    r'(?i)\bSTATUE\s*CRUISES.*': 'Travel.NewYorkMarch2024',
    r'(?i)\b911\s*MEMORIAL.*': 'Travel.NewYorkMarch2024',
    r'(?i)\bNEW\s*YORK\s*NY': 'Travel.NewYorkMarch2024',
    r'(?i)\bQUEENS\s*NY': 'Travel.NewYorkMarch2024',
    r'(?i).*FLUSHING\s*NY': 'Travel.NewYorkMarch2024',
    r'(?i)\bLONG\s*ISLAND.*NY': 'Travel.NewYorkMarch2024',
    r'(?i)\bLGA\s*BROOKLYN\s*DINER': 'Travel.NewYorkMarch2024',
    r'(?i)\bUBER\s*TRIP': 'Travel.NewYorkMarch2024',
    r'(?i)\bEAST\s*ELMHURST.*NY': 'Travel.NewYorkMarch2024',
#endregion Travel - Specific Trips
#region Unknowns, one-offs (applied last)
    r'(?i)\bHOMESENSE.*': 'Unknown.HomeSense',
    r'(?i)\bPRESSNET.*': 'Unknown.PressNet',
    r'(?i)\bBUYGOODS.*': 'Unknown.BuyGoods',
    r'(?i)\bPAYPAL\s\*AAAA\s*EMBROI.*': 'Unknown.AAAA EMBROI',
    r'(?i)\bID:DIGISTORE\d\d\b': 'Unknown.DIGISTORE',
    r'(?i).*VIRTUALCHARGES\.COM.*': 'Unknown.VirtualChargesDotCom',
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
    r'(?i)\bAPPLE\s*STORE.*08\/27.*': 'Temp.Blackmail.Apple Gift Card',
    r'(?i)\bAPPLE\s*STORE.*08\/29.*': 'Temp.Blackmail.Apple Gift Card',
    r'(?i).*FFNHELP\.COM.*': 'Unknown.FFNHELP.COM',
    r'(?i).*GEDMATCH.*': 'Unknown.GEDMATCH',
    r'(?i).*DJO-CMF.*': 'Unknown.DJO-CMF',
    r'(?i)\bSNIFFIES.*': 'Temp.Chat Site',
    r'(?i).*VTSUP\.COM.*AMSTERDAM.*': 'Temp.Chat Site',
    r'(?i).*SRFBM\.COM.*PERNIK.*': 'Temp.Chat Site',
    r'(?i)\bZelle\s*payment\s*to.*Thomas\s*Wikstrom.*': 'Temp.Chat Fraud',
    r'(?i).*BeenVerified.*': 'Temp.Fraud Search.BeenVerified-com',
    r'(?i).*REVERSEPHONE.*': 'Temp.Fraud Search.ReversePhone-com',
    r'(?i).*SOCIALCATFISH.*': 'Temp.Fraud Search.SocialCatfish-com',
    r'(?i).*.*CASH\s*APP\*AMIE.*': 'Temp.Massage',
    r'(?i)\b7-ELEVEN\s.*?MOBILE\sPURCHASE\b': 'Temp.Vape',
#endregion Unknowns, one-offs (applied last)
#region Checks categorized manually by number - run last
    r'(?i)\bCheck\s*x*\d*\b': 'Banking.Checks to Categorize'
#endregion Checks categorized manually by number - run last
#endregion Non-Essential Spending Categories
}
compiled_category_map = {
    re.compile(pattern, re.IGNORECASE): category 
    for pattern, category in category_map.items()
}
#endregion category_map
# ---------------------------------------------------------------------------- +
#region category_histogram
class CategoryCounter(dict):
    """A custom dictionary to count occurrences of budget categories."""
    def __missing__(self, key):
        return 0
    def count(self, key: str) -> str:
        """Increment the count for key, return key."""
        self[key] += 1
        return key
category_histogram : Optional[CategoryCounter] = None

def get_category_histogram() -> CategoryCounter:
    """Get the category histogram, initializing it if necessary."""
    global category_histogram
    if category_histogram is None:
        category_histogram = CategoryCounter()
    return category_histogram

def clear_category_histogram():
    """Clear the category histogram."""
    global category_histogram
    category_histogram = CategoryCounter()
    return category_histogram
#endregion category_histogram
# ---------------------------------------------------------------------------- +
