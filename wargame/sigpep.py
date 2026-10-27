"""Strict parsing shared by the L3 graders (logic follows the sample's t4 grader)."""
from wargame.strictjson import AnswerError, is_finite_number, is_int, load_answer

BAR = 0.71


def parse(obj, expected_ids):
    if type(obj) is not dict:
        raise AnswerError("answer must be a JSON object")
    extra = sorted(set(obj) - {"lengths", "accuracy"})
    if "lengths" not in obj or extra:
        raise AnswerError("answer needs 'lengths' and may hold 'accuracy', nothing else")
    lengths = obj["lengths"]
    if type(lengths) is not dict or set(lengths) != expected_ids:
        raise AnswerError("lengths must cover exactly the 20 proteins")
    for p, v in lengths.items():
        if not is_int(v) or v < 0:
            raise AnswerError(f"length for {p} must be a non-negative integer")
    acc = obj.get("accuracy")
    if acc is not None and (not is_finite_number(acc) or not 0 <= acc <= 1):
        raise AnswerError("accuracy must be a number in [0, 1]")
    return lengths, acc


def load(answer_path, key):
    return parse(load_answer(answer_path), set(key))


def measured_accuracy(lengths, key):
    return sum(lengths[p] == key[p] for p in key) / len(key)
