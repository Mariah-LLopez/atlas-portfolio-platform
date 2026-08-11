import numpy as np

from atlas.portfolio.baseline import equal_weight


def test_equal_weight_sums_to_one():
    weights = equal_weight(["A", "B", "C", "D"])
    assert np.isclose(weights.sum(), 1.0)


def test_equal_weight_is_equal():
    weights = equal_weight(["A", "B"])
    assert np.isclose(weights["A"], 0.5)
    assert np.isclose(weights["B"], 0.5)
