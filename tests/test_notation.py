import unittest

from diceconv.notation import (
    DiceTerm,
    ModifierTerm,
    NotationError,
    format_notation,
    parse_notation,
    spec_from_dict,
    spec_to_dict,
)


class ParseNotationTests(unittest.TestCase):
    def test_single_dice_term(self):
        terms = parse_notation("2d6")
        self.assertEqual(terms, [DiceTerm(count=2, sides=6, sign=1)])

    def test_omitted_count_defaults_to_one(self):
        terms = parse_notation("d20")
        self.assertEqual(terms, [DiceTerm(count=1, sides=20, sign=1)])

    def test_case_insensitive_d(self):
        terms = parse_notation("2D6")
        self.assertEqual(terms, [DiceTerm(count=2, sides=6, sign=1)])

    def test_mixed_dice_and_modifiers(self):
        terms = parse_notation("2d6+1d4-3")
        self.assertEqual(
            terms,
            [
                DiceTerm(count=2, sides=6, sign=1),
                DiceTerm(count=1, sides=4, sign=1),
                ModifierTerm(value=3, sign=-1),
            ],
        )

    def test_leading_sign_is_optional(self):
        self.assertEqual(parse_notation("2d6"), parse_notation("+2d6"))

    def test_leading_negative_sign(self):
        terms = parse_notation("-2d6+3")
        self.assertEqual(
            terms,
            [DiceTerm(count=2, sides=6, sign=-1), ModifierTerm(value=3, sign=1)],
        )

    def test_whitespace_is_ignored(self):
        terms = parse_notation(" 2d6 + 3 ")
        self.assertEqual(
            terms,
            [DiceTerm(count=2, sides=6, sign=1), ModifierTerm(value=3, sign=1)],
        )

    def test_empty_string_raises(self):
        with self.assertRaises(NotationError):
            parse_notation("")

    def test_dangling_sign_raises(self):
        with self.assertRaises(NotationError):
            parse_notation("2d6+")

    def test_unrecognised_term_raises(self):
        with self.assertRaises(NotationError):
            parse_notation("2d6x")

    def test_zero_count_raises(self):
        with self.assertRaises(NotationError):
            parse_notation("0d6")

    def test_zero_sides_raises(self):
        with self.assertRaises(NotationError):
            parse_notation("d0")

    def test_double_sign_raises(self):
        with self.assertRaises(NotationError):
            parse_notation("2d6++3")


class FormatNotationTests(unittest.TestCase):
    def test_round_trip(self):
        text = "2d6+1d4-3"
        self.assertEqual(format_notation(parse_notation(text)), text)

    def test_single_die_count_is_omitted(self):
        terms = [DiceTerm(count=1, sides=20, sign=1)]
        self.assertEqual(format_notation(terms), "d20")

    def test_leading_negative_term_keeps_its_sign(self):
        terms = [DiceTerm(count=2, sides=6, sign=-1), ModifierTerm(value=3, sign=1)]
        self.assertEqual(format_notation(terms), "-2d6+3")

    def test_empty_terms_raises(self):
        with self.assertRaises(NotationError):
            format_notation([])


class SpecDictTests(unittest.TestCase):
    def test_round_trip_through_dict(self):
        terms = parse_notation("2d6+1d4-3")
        rebuilt = spec_from_dict(spec_to_dict(terms))
        self.assertEqual(terms, rebuilt)

    def test_missing_terms_key_raises(self):
        with self.assertRaises(NotationError):
            spec_from_dict({})

    def test_non_dict_input_raises(self):
        with self.assertRaises(NotationError):
            spec_from_dict(["not", "a", "dict"])

    def test_unknown_term_type_raises(self):
        with self.assertRaises(NotationError):
            spec_from_dict({"terms": [{"type": "explosion", "value": 1}]})

    def test_sign_defaults_to_positive(self):
        terms = spec_from_dict({"terms": [{"type": "modifier", "value": 5}]})
        self.assertEqual(terms, [ModifierTerm(value=5, sign=1)])


if __name__ == "__main__":
    unittest.main()
