"""Strict parsing and Spearman scoring shared by the L2 graders (logic follows the sample's t2 grader)."""
from wargame.stats import spearman
from wargame.strictjson import AnswerError, is_finite_number, load_answer, require_keys

BAR = 0.66


def parse(obj, expected_ids):
    require_keys(obj, ["predictions"])
    preds = obj["predictions"]
    if type(preds) is not dict:
        raise AnswerError("predictions must be an object mapping variant to score")
    if set(preds) != expected_ids:
        raise AnswerError("predictions must cover exactly the test variants")
    for v, x in preds.items():
        if not is_finite_number(x):
            raise AnswerError(f"prediction for {v} is not a finite number")
    return preds


def rho(answer_path, truth):
    ids = sorted(truth)
    preds = parse(load_answer(answer_path), set(ids))
    return spearman([float(preds[v]) for v in ids], [truth[v] for v in ids])
