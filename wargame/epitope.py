"""Strict epitope checking used by the patched graders of L0 and L1 (logic follows the sample's t1 grader)."""
from wargame.strictjson import AnswerError, is_finite_number, is_int, load_answer, require_keys

ITEM_KEYS = ["chain", "resnum", "resname", "min_distance"]
DIST_TOL = 0.01


def parse(obj):
    require_keys(obj, ["epitope"])
    items = obj["epitope"]
    if type(items) is not list:
        raise AnswerError("epitope must be a list")
    out = {}
    for i, it in enumerate(items):
        where = f"epitope[{i}]"
        require_keys(it, ITEM_KEYS, where)
        if type(it["chain"]) is not str or type(it["resname"]) is not str:
            raise AnswerError(f"{where}: chain and resname must be strings")
        if not is_int(it["resnum"]):
            raise AnswerError(f"{where}: resnum must be an integer")
        if not is_finite_number(it["min_distance"]) or it["min_distance"] < 0:
            raise AnswerError(f"{where}: min_distance must be a finite non-negative number")
        rid = (it["chain"], it["resnum"])
        if rid in out:
            raise AnswerError(f"duplicate residue {rid}")
        out[rid] = (it["resname"], float(it["min_distance"]))
    return out


def residue_errors(ans, key):
    """Residues present in both whose name or distance is wrong."""
    bad = 0
    for rid in set(ans) & set(key):
        (an, ad), (kn, kd) = ans[rid], key[rid]
        if an != kn or abs(ad - kd) > DIST_TOL + 1e-9:
            bad += 1
    return bad


def load_strict(answer_path):
    return parse(load_answer(answer_path))
