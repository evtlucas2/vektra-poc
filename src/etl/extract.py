import xml.etree.ElementTree as ET
from pathlib import Path


def extract_transactions(path: Path) -> list[dict]:
    """Parse an OFX file and return raw STMTTRN data as a list of dicts."""
    content = path.read_text(encoding="latin-1", errors="replace")
    ofx_start = content.lower().find("<ofx>")
    if ofx_start == -1:
        raise ValueError(f"No <OFX> tag found in {path}")
    xml_body = content[ofx_start:]
    root = ET.fromstring(xml_body)
    rows = []
    for txn in root.iter("STMTTRN"):
        row = {
            "DTPOSTED": (txn.findtext("DTPOSTED") or "").strip(),
            "TRNAMT": (txn.findtext("TRNAMT") or "").strip(),
            "NAME": (txn.findtext("NAME") or "").strip(),
            "MEMO": (txn.findtext("MEMO") or "").strip(),
        }
        rows.append(row)
    return rows
