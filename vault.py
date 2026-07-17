from pathlib import Path
from pyomd import Notes
from pyomd.metadata import MetadataType
from typing import List, Dict
import decimal


# Source - https://stackoverflow.com/a
# Posted by Torxed, modified by community. See post 'Timeline' for change history
# Retrieved 2025-12-06, License - CC BY-SA 3.0


def safe_round(value, digits=2, symbol=None, label=""):
    try:
        return round(value, digits)
    except (TypeError, ValueError):
        if symbol:
            print(f"{label} set to 0 for {symbol}")
        return 0


class vault:
    def __init__(self):
        pass

    def filter(self, path, data_list):
        self.path = path
        notes = Notes(path)
        notes.filter(has_meta=[("Symbol", None, MetadataType.FRONTMATTER), ("Aktien", None, MetadataType.FRONTMATTER)])

        for n in notes.notes:
            data = {}
            data['note'] = n

            symbol = n.metadata.get('Symbol', MetadataType.FRONTMATTER)[0]
            data['symbol'] = symbol
            data_list.append(data)
        print(f"Notes filtered: {len(notes.notes)}")

    def fill_notes(self, data_list):
        for d in data_list:
            symbol = d['symbol']
            n = d['note']

            if 'price' not in d:
                print(f"Ueberspringe {symbol}: keine Kursdaten verfuegbar")
                continue

            try:
                self._fill_note(d)
            except Exception as e:
                print(f"Fehler beim Befuellen der Notiz fuer {symbol}: {e}")

    def _fill_note(self, d):
        symbol = d['symbol']
        n = d['note']
        kurs = d['price']
        kurs_perf = d['change']
        week52 = d.get('change52Week')
        avg200 = d.get('avg200')
        high52 = d.get('fiftyTwoWeekHigh')

        print(f"{symbol}: {kurs}")
        n.metadata.add('stPrice', round(kurs, 2), MetadataType.FRONTMATTER, overwrite=True)
        n.metadata.add('st1Day', round(kurs_perf, 1), MetadataType.FRONTMATTER, overwrite=True)

        kgv = d.get('trailingPE')
        if isinstance(kgv, (int, float)):
            n.metadata.add('kgv', round(kgv, 1), MetadataType.FRONTMATTER, overwrite=True)

        week52 = safe_round(week52, 2, symbol, "week52")
        n.metadata.add('st52week', week52, MetadataType.FRONTMATTER, overwrite=True)

        avg200 = safe_round(avg200, 2, symbol, "avg200")
        n.metadata.add('stAvg200', avg200, MetadataType.FRONTMATTER, overwrite=True)

        try:
            dd = (high52 - kurs) / high52
        except (TypeError, ZeroDivisionError):
            dd = None

        if dd is not None:
            n.metadata.add('stDrawdown', round(dd * 100, 1), MetadataType.FRONTMATTER, overwrite=True)

        self._apply_trigger(n, symbol, kurs, kgv, avg200, week52, dd, high52)

    def _apply_trigger(self, n, symbol, kurs, kgv, avg200, week52, dd, high52):
        try:
            trigger = n.metadata.get("Trigger", MetadataType.FRONTMATTER)[0]
        except (KeyError, IndexError, TypeError):
            trigger = ""

        if not trigger:
            return

        trigger_vars = {
            'kurs': kurs,
            'kgv': kgv if isinstance(kgv, (int, float)) else None,
            'avg200': avg200,
            'week52': week52,
            'dd': dd,
            'high52': high52,
        }

        try:
            result = eval(trigger.lower(), {"__builtins__": {}}, trigger_vars)
            if result is True:
                n.metadata.add('Kommentar', f"Triggered {trigger}", MetadataType.FRONTMATTER, overwrite=True)
                n.metadata.add('check', True, MetadataType.FRONTMATTER, overwrite=True)
        except Exception as e:
            print(f"Trigger-Fehler bei {symbol}: '{trigger}' -> {e}")
            n.metadata.add('Kommentar', f"Fehler in Trigger-Formel: {e}", MetadataType.FRONTMATTER, overwrite=True)

    def write_notes(self, data_list):
        for d in data_list:
            n = d['note']
            symbol = d.get('symbol', '?')
            try:
                n.update_content(inline_inplace=False, inline_position="top", inline_tml="callout")  # type: ignore
                n.write()
            except Exception as e:
                print(f"Fehler beim Schreiben der Notiz fuer {symbol}: {e}")
