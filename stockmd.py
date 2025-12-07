from pathlib import Path
from vault import vault
from yahoodata import yahoodata



"""
Main:
    read symbols from vault
    read info for symbols
    fill info to notes in vault


vault:
    filter notes 
    create symbols list
    fill info to notes
    store notes

stocksource:
    read info for symbols

"""

#path = Path("c:\\workspace_c\\obsidian\\aktien-vault\\")
path = Path("C:\\Users\\anton\\Sync\\Winkel3\\21 Docu\\Finanz\\")


data_list = []

my_vault = vault()
my_vault.filter(path, data_list)

yahoo = yahoodata()

symbols = [d['symbol'] for d in data_list]

yahoo.load_info(symbols)

yahoo.extract_info(data_list)


my_vault.fill_notes(data_list)
my_vault.write_notes(data_list)




