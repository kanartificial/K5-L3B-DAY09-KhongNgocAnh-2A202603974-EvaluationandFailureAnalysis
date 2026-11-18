"""Regression test from trace case C-002@11 (FM-03: ticket_trust / model_override)."""
from __future__ import annotations

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9.graders import DbFactKept, RefundAmountCorrect
from lab9.trace_case import investigate

pytestmark = pytest.mark.student


def _eval_case(shape: str) -> tuple[dict, bool, bool]:
    case = investigate(shape, "C-002", 11)
    ctx = EvaluatorContext(
        name=f"{shape}-C-002@11",
        inputs={"claim_id": "C-002", "seed": 11},
        metadata=None,
        expected_output=case["label"],
        output=case["trial"],
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )
    db_kept = bool(DbFactKept().evaluate(ctx).value)
    amt_ok = bool(RefundAmountCorrect().evaluate(ctx).value)
    return case, db_kept, amt_ok


def test_c002_fixed_passes_and_does_not_override_db():
    case, db_kept, amt_ok = _eval_case("fixed")
    assert case["trial"]["lab8_pass"] is True
    assert db_kept is True
    assert amt_ok is True


def test_c002_seeded_regression_is_caught_by_db_fact_and_refund():
    case, db_kept, amt_ok = _eval_case("seeded_regression")
    assert case["trial"]["lab8_pass"] is False
    assert db_kept is False
    assert amt_ok is False
