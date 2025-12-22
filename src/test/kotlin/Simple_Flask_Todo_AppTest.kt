# test_fee_estimator.py

from my_project.fee_estimator import FeeEstimator
import pytest

@pytest.fixture
def fee_estimator():
    return FeeEstimator()

class TestFeeEstimator:
    def test_estimate_fee_with_valid_inputs(self, fee_estimator):
        # Given
        base_fee = 100
        fee_multiplier = 2
        additional_fee = 50
        expected_fee = 100 * 2 + 50  # Expected: 100 * 2 + 50 = 200 + 50 = 250

        # When
        result = fee_estimator.estimate_fee(base_fee, fee_multiplier, additional_fee)

        # Then
        assert result == expected_fee, f"Expected fee should be {expected_fee}, got {result}"

    def test_estimate_fee_with_zero_base(self, fee_estimator):
        # Given
        base_fee = 0
        fee_multiplier = 5
        additional_fee = 0
        expected_fee = 0 * 5 + 0  # Expected: 0

        # When
        result = fee_estimator.estimate_fee(base_fee, fee_multiplier, additional_fee)

        # Then
        assert result == expected_fee, f"Expected fee should be {expected_fee}, got {result}"

    def test_estimate_fee_negative_values(self, fee_estimator):
        # Given
        base_fee = -100
        fee_multiplier = 2
        additional_fee = 50

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            fee_estimator.estimate_fee(base_fee, fee_multiplier, additional_fee)

        # Verify exception message
        assert str(exc_info.value) == "Base fee cannot be negative", "Exception message should match"

    def test_estimate_fee_large_values(self, fee_estimator):
        # Given
        base_fee = 1000000
        fee_multiplier = 10
        additional_fee = 100000
        expected_fee = 1000000 * 10 + 100000  # Expected: 10000000 + 100000 = 10100000

        # When
        result = fee_estimator.estimate_fee(base_fee, fee_multiplier, additional_fee)

        # Then
        assert result == expected_fee, f"Expected fee should be {expected_fee}, got {result}"
