"""Strict parsing for the GO-table graders (logic follows the sample's t3 grader)."""
import re

from wargame.strictjson import AnswerError, is_finite_number, is_int, require_keys

GO_RE = re.compile(r"GO:\d{7}")
REL_TOL = 1e-4


def parse_table(obj):
    require_keys(obj, ["N", "n", "m", "terms"])
    for f in ("N", "n", "m"):
        if not is_int(obj[f]) or obj[f] < 0:
            raise AnswerError(f"{f} must be a non-negative integer")
    if type(obj["terms"]) is not list:
        raise AnswerError("terms must be a list")
    out = {}
    for i, t in enumerate(obj["terms"]):
        require_keys(t, ["go_id", "k", "K", "q"], f"terms[{i}]")
        if type(t["go_id"]) is not str or not GO_RE.fullmatch(t["go_id"]):
            raise AnswerError(f"terms[{i}]: go_id must look like GO:0000000")
        if not is_int(t["k"]) or not is_int(t["K"]):
            raise AnswerError(f"terms[{i}]: k and K must be integers")
        if not is_finite_number(t["q"]) or not 0 <= t["q"] <= 1:
            raise AnswerError(f"terms[{i}]: q must be a finite number in [0, 1]")
        gid = t["go_id"]
        if gid in out:
            raise AnswerError(f"duplicate term {gid}")
        out[gid] = (t["k"], t["K"], float(t["q"]))
    return (obj["N"], obj["n"], obj["m"]), out


def tables_match(a, k):
    (ah, at), (kh, kt) = a, k
    if ah != kh or set(at) != set(kt):
        return False
    for t in kt:
        if at[t][:2] != kt[t][:2] or abs(at[t][2] - kt[t][2]) > REL_TOL * kt[t][2]:
            return False
    return True
