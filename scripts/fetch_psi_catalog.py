"""Download NASA PSI metadata and experiment tables for every Combustion Science investigation.

Writes (both committed, CC0 NASA data, so the site builds offline):
  data/source/psi/catalog/<PSI-NN>.json   the PSI fields Flare AI uses, copied verbatim, plus retrieval date
  data/source/psi/tables/<file>.csv       each investigation's "Experimental table" exactly as NASA serves it

Run only when you want to refresh from NASA (needs network access to psi.nasa.gov):
  python scripts/fetch_psi_catalog.py
"""
import json
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT = ROOT / "data" / "source" / "psi" / "catalog"
TAB = ROOT / "data" / "source" / "psi" / "tables"
API = "https://psi.nasa.gov/geode-py/ws"
KEEP = ["accession", "investigationAcronym", "title", "doi", "licenseIdentifier", "releaseDate", "version", "researchArea",
        "subResearchArea", "projectType", "flightProgram", "experimentHardware", "experimentHardwareLink",
        "investigationStartDate", "investigationEndDate", "objective", "approach", "hypothesis", "researchImpacts"]


def get(url):
    return urllib.request.urlopen(url, timeout=90).read()


def main():
    CAT.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    hits = json.loads(get(API + "/repo/search?term=&source=psi&type=investigation&size=500"))["hits"]["hits"]
    accs = sorted((h["_source"]["Accession"] for h in hits if "Combustion" in h["_source"].get("Research Area", "")),
                  key=lambda a: int(a.split("-")[1]))
    for acc in accs:
        d = json.loads(get(f"{API}/repo/investigations/{acc}"))
        out = {k: d.get(k, "") for k in KEEP}
        out["publications"] = [{"title": p.get("title", ""), "authors": p.get("authorList", ""), "doi": p.get("doi", ""),
                                "year": str(p.get("year", "") or "")} for p in (d.get("publications") or [])]
        out["tables"] = []
        for t in d.get("experimentalTable") or []:
            name = t["file_name"]
            signed = get(f"{API}/studies/{acc}/download?" + urllib.parse.urlencode({"file": name, "redirect": "false"})).decode().strip().strip('"')
            (TAB / name).write_bytes(get(signed))
            out["tables"].append(name)
        out["retrieved"] = date.today().isoformat()
        out["landing_page"] = f"https://psi.nasa.gov/physci/repo/data/investigations/{acc}"
        (CAT / f"{acc}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print(acc, out["investigationAcronym"] or out["title"][:40], len(out["tables"]), "tables")


if __name__ == "__main__":
    main()
