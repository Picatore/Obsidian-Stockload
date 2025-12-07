from pathlib import Path
from pyomd import Notes
from pyomd.metadata import MetadataType
from typing import List, Dict
import decimal


# Source - https://stackoverflow.com/a
# Posted by Torxed, modified by community. See post 'Timeline' for change history
# Retrieved 2025-12-06, License - CC BY-SA 3.0



class vault:
    def __init__(self):
        pass        

    def filter(self, path, list):
        self.path = path
        notes = Notes(path)
        notes.filter(has_meta=[("Symbol",None,MetadataType.FRONTMATTER), ("Aktien",None,MetadataType.FRONTMATTER)])

        for n in notes.notes:
            data = {}
            data['note'] = n

            symbol = n.metadata.get('Symbol', MetadataType.FRONTMATTER)[0]
            data['symbol'] = symbol
            list.append(data)
        print(f"Notes filtered: {len(notes.notes)}")

    def fill_notes(self, list):
        for d in list:
            symbol = d['symbol']
            n = d['note']
            kurs = d['price']
            kurs_perf = d['change']
            week52 = d.get('change52Week')
            avg200 = d.get('avg200')
            high52 = d.get('fiftyTwoWeekHigh')
            dd = (high52-kurs)/high52
            print(f"{symbol}: {kurs}")
            n.metadata.add('stPrice', round(kurs,2), MetadataType.FRONTMATTER, overwrite=True)
            n.metadata.add('st1Day', round(kurs_perf,1), MetadataType.FRONTMATTER, overwrite=True)

            kgv = d.get('trailingPE')
            if isinstance(kgv, float):
                n.metadata.add('kgv', round(kgv,1), MetadataType.FRONTMATTER, overwrite=True)
            

            try:
                week52 = round(week52,2)
            except:
                print(f"avg set to 0 for {symbol}")
                week52 = 0
            n.metadata.add('st52week', round(week52,2), MetadataType.FRONTMATTER, overwrite=True)

            try:
                avg200 = round(avg200,2)
            except:
                avg200 = 0
                print(f"avg200 set to 0 for {symbol}")
            n.metadata.add('stAvg200', round(avg200,2), MetadataType.FRONTMATTER, overwrite=True)

            # handle Trigger formula parsing
            try:
                trigger = n.metadata.get("Trigger", MetadataType.FRONTMATTER)[0]
            except:
                trigger = ""

            if trigger != "":
                try:
                    result = eval(trigger.lower())
                    if result == True:
                        n.metadata.add('Kommentar', "Triggered "+trigger, MetadataType.FRONTMATTER, overwrite=True)
                        n.metadata.add('check', True, MetadataType.FRONTMATTER, overwrite=True)
                except:
                    n.metadata.add('Kommentar', "Error! "+trigger, MetadataType.FRONTMATTER, overwrite=True)




    def write_notes(self, list):
        for d in list:
            n = d['note']
            n.update_content(inline_inplace=False, inline_position="top", inline_tml="callout") #type: ignore
            n.write()






