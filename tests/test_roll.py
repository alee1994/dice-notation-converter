import random
import unittest

from diceconv.notation import NotationError, parse_notation
from diceconv.roll import format_result, roll_terms


class FixedRng:
    """Stands in for random.Random, returning a scripted sequence of dice."""

    def __init__(self, values):
        self.values = list(values)

    def randint(self, low, high):
        value = self.values.pop(0)
        assert low <= value <= high
        return value


class RollTermsTests(unittest.TestCase):
    def test_sums_dice_and_modifier(self):
        result = roll_terms(parse_notation("2d6+3"), FixedRng([4, 5]))
        self.assertEqual(result.total, 12)

    def test_negative_terms_subtract(self):
        result = roll_terms(parse_notation("1d8-1d4-2"), FixedRng([7, 3]))
        self.assertEqual(result.total, 2)

    def test_keep_highest_drops_lowest(self):
        result = roll_terms(parse_notation("4d6kh3"), FixedRng([2, 6, 3, 5]))
        self.assertEqual(result.total, 14)
        self.assertEqual(sorted(result.parts[0].dropped), [2])

    def test_keep_lowest(self):
        result = roll_terms(parse_notation("d20dis"), FixedRng([15, 4]))
        self.assertEqual(result.total, 4)

    def test_exploding_adds_extra_dice(self):
        result = roll_terms(parse_notation("1d6!"), FixedRng([6, 6, 2]))
        self.assertEqual(result.parts[0].kept, [6, 6, 2])
        self.assertEqual(result.total, 14)

    def test_exploding_one_sided_die_raises(self):
        with self.assertRaises(NotationError):
            roll_terms(parse_notation("1d1!"))

    def test_seeded_rolls_repeat(self):
        terms = parse_notation("6d10+2")
        first = roll_terms(terms, random.Random(7))
        second = roll_terms(terms, random.Random(7))
        self.assertEqual(first.total, second.total)

    def test_totals_stay_in_range(self):
        terms = parse_notation("3d6")
        rng = random.Random(1)
        for _ in range(200):
            self.assertTrue(3 <= roll_terms(terms, rng).total <= 18)


class FormatResultTests(unittest.TestCase):
    def test_breakdown_and_total(self):
        result = roll_terms(parse_notation("4d6kh3-1"), FixedRng([2, 6, 3, 5]))
        self.assertEqual(
            format_result(result),
            "4d6kh3  [6, 3, 5] dropped [2] = 14\n-1\ntotal: 13",
        )

    def test_positive_later_term_has_plus(self):
        result = roll_terms(parse_notation("1d6+2"), FixedRng([3]))
        self.assertEqual(format_result(result), "d6  [3] = 3\n+2\ntotal: 5")


if __name__ == "__main__":
    unittest.main()
