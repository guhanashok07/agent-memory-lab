from memlab.label import agreement
from memlab.session import apply_ops


def test_curation_applies_valid_ops_and_rejects_the_rest():
    memory = [{"id": 1, "text": "old"}]
    ops = [
        {"op": "UPDATE", "id": 1, "text": "new"},
        {"op": "ADD", "text": "second"},
        {"op": "DELETE", "id": 99},
        {"op": "ADD", "text": "  "},
    ]
    memory, next_id, applied, rejected = apply_ops(memory, ops, next_id=2)
    assert memory == [{"id": 1, "text": "new"}, {"id": 2, "text": "second"}]
    assert next_id == 3
    assert len(applied) == 2 and len(rejected) == 2


def test_curation_can_delete():
    memory, _, _, _ = apply_ops([{"id": 1, "text": "x"}], [{"op": "DELETE", "id": 1}], next_id=2)
    assert memory == []


def test_kappa_is_one_on_perfect_agreement():
    labels = {"a": "episodic", "b": "procedural", "c": "semantic"}
    assert agreement(labels, labels) == {"n": 3, "percent": 100.0, "kappa": 1.0}
