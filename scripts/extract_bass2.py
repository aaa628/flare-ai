"""Draft extractor for NASA/TM-2021-011385 (BASS-II Summary Report), Appendix A.

Reads the plain-text version of the PDF and writes DRAFT rows. Nothing here is
verified: every row needs a human to check it against the PDF page named in
`source_page` before `verified_by` / `verified_date` are filled in.

Usage: python scripts/extract_bass2.py
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "source" / "TM-20210011385.txt"
OUT = ROOT / "data" / "bass2_draft.csv"

PI = {"B": "Bhattacharjee", "F": "Ferkul", "P": "Fernandez-Pello",
      "M": "Miller", "O": "Olson", "T": "T'ien"}
TOK = r"(\S+)"
# Anchor on the camera "shutter hold" column (Cont / Man / "7 s"), then:
# frames shot, total frames, then 8 gas readings: O2 calibrated init/final,
# O2 raw init/final, CO2 init/final, CO init/final. Tokens are kept exactly as
# printed (NASA's tables contain entries such as "+OR", ">500", "failed").
TAIL = re.compile(
    r"\b(?:Cont|Man|\d+ ?s)\s+(\d+)\s+" + TOK + r"\s+" + r"\s+".join([TOK] * 8)
    + r"(?:\s+|$)")
ANCHOR = re.compile(r"(?:^|\s)(?:(\d+)\s+)?([BFPMOT]\d{1,2}[ab]?)\s+(\d{1,3}[mMLl]?)\s+(.*)")
DATE_START = re.compile(r"^\s*\d{1,2}/\d{1,2}/\d{2,4}")
STOP = re.compile(r"^(NASA/TM|TABLE |A\.\d |Appendix B)")
FOOT = re.compile(r"^[a-h]$")
PAGE = re.compile(r"^NASA/TM-20210011385\s+(\d+)")
# Rows whose printed layout defeats the pattern. Values keyed by hand from the
# raw text (see raw_text column); marked parse_ok="manual" so they get extra scrutiny.
# order: O2 cal init/final, O2 raw init/final, CO2 init/final, CO init/final
MANUAL = {
    "BASSII-M5": ["22.2", "19.0", "20.6", "17.4", "0.44", "3.22", "9", ">500"],
    "BASSII-O16": ["14.5", "14.5", "13.4", "13.4", "0.27", "0.32", "2", "33"],
    "BASSII-T3": ["17.2", "16.8", "16.3", "15.9", "0.42", "0.7", "45", "113"],
}
MODE = re.compile(r"\b(Opposed|Concurrent|Stagnation)\b")


def clean(v):
    v = v.strip()
    return "" if re.fullmatch(r"-+|none", v) else v


def main():
    lines = SRC.read_text(errors="replace").splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.startswith("Appendix A.—Test Matrices") and i > 3000)
    end = next(i for i, l in enumerate(lines)
               if i > start and l.startswith("Appendix B.—"))
    page = ""
    for k in range(start, 0, -1):
        mp = PAGE.match(lines[k])
        if mp:
            page = mp.group(1)
            break
    rows = []
    i = start
    while i < end:
        m_page = PAGE.match(lines[i])
        if m_page:
            page = m_page.group(1)
        m = ANCHOR.search(lines[i])
        if not m or lines[i].startswith(("TABLE", "Actual")):
            i += 1
            continue
        block = [lines[i]]
        j = i + 1
        while j < end and not (DATE_START.match(lines[j]) or STOP.match(lines[j])
                               or FOOT.match(lines[j].strip())
                               or ANCHOR.search(lines[j])):
            block.append(lines[j])
            j += 1
        text = " ".join(b.strip() for b in block)
        a = ANCHOR.search(text)
        as_run, tid, sample, rest = a.groups()
        t = TAIL.search(rest)
        rec = {"id": f"BASSII-{tid}", "pi": PI[tid[0]], "as_run_no": as_run or "",
               "sample_no": sample, "source_page": page, "raw_text": text}
        if t:
            before, after = rest[:t.start()], rest[t.end():]
            vals = [clean(x) for x in t.groups()[1:]]
            rec.update(frames_shot=clean(t.group(1)), total_frames=vals[0],
                       o2_cal_initial=vals[1], o2_cal_final=vals[2],
                       o2_raw_initial=vals[3], o2_raw_final=vals[4],
                       co2_initial=vals[5], co2_final=vals[6],
                       co_initial_ppm=vals[7], co_final_ppm=vals[8],
                       observation=after.strip(), parse_ok="yes")
        else:
            before = rest
            rec.update(observation="", parse_ok="NO")
        if rec["parse_ok"] == "yes":
            try:
                ok = 5 <= float(rec["o2_cal_initial"]) <= 30
            except ValueError:
                ok = False
            if not ok:  # columns probably shifted: a human must key this row
                rec["parse_ok"] = "CHECK"
        if rec["id"] in MANUAL:
            v = MANUAL[rec["id"]]
            tail_txt = " ".join(v)
            k = rest.find(tail_txt)
            assert k >= 0, rec["id"]
            (rec["o2_cal_initial"], rec["o2_cal_final"], rec["o2_raw_initial"],
             rec["o2_raw_final"], rec["co2_initial"], rec["co2_final"],
             rec["co_initial_ppm"], rec["co_final_ppm"]) = v
            rec["observation"] = rest[k + len(tail_txt):].strip()
            rec["parse_ok"] = "manual"
        mm = MODE.search(before)
        rec["flow_mode"] = mm.group(1) if mm else ""
        ig = re.search(r"\b(Integral|Integrated)\b", before)
        rec["material_raw"] = before[:ig.start()].strip() if ig else before[:60]
        rec["setup_raw"] = before[ig.start():].strip() if ig else ""
        flags = []
        if not rec["flow_mode"]:
            flags.append("flow_mode_not_stated")
        try:
            if abs(float(rec["o2_cal_final"]) - float(rec["o2_cal_initial"])) > 3:
                flags.append("o2_final_reading_suspect")
        except ValueError:
            flags.append("o2_final_not_numeric")
        if rec["parse_ok"] == "manual":
            flags.append("hand_keyed")
        rec["qc_flag"] = ";".join(flags)
        rows.append(rec)
        i = j
    cols = ["id", "pi", "as_run_no", "sample_no", "material_raw", "flow_mode",
            "o2_cal_initial", "o2_cal_final", "o2_raw_initial", "o2_raw_final",
            "co2_initial", "co2_final", "co_initial_ppm", "co_final_ppm",
            "observation", "setup_raw", "source_page", "qc_flag", "parse_ok",
            "verified_by", "verified_date", "verifier_notes", "raw_text"]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
