import unittest
from pymining import itemmining, perftesting, assocrules


class TestAssocRule(unittest.TestCase):

    def testDefaultSupportConf(self):
        ts1 = perftesting.get_default_transactions()
        relim_input = itemmining.get_relim_input(ts1)
        report = itemmining.relim(relim_input, 2)
        rules = assocrules.mine_assoc_rules(report, min_support=2)
        self.assertEqual(23, len(rules))

        a_rule = (frozenset(['b', 'e']), frozenset(['d']), 2, 1.0)
        self.assertTrue(a_rule in rules)

        ts2 = perftesting.get_default_transactions_alt()
        relim_input = itemmining.get_relim_input(ts2)
        report = itemmining.relim(relim_input, 2)
        rules = assocrules.mine_assoc_rules(report, min_support=2)
        self.assertEqual(29, len(rules))

        a_rule = (frozenset(['e']), frozenset(['a', 'd']), 2, 2.0/3.0)
        self.assertTrue(a_rule in rules)

    def testConfidence075(self):
        ts1 = perftesting.get_default_transactions()
        relim_input = itemmining.get_relim_input(ts1)
        report = itemmining.relim(relim_input, 2)
        rules = assocrules.mine_assoc_rules(
            report, min_support=2, min_confidence=0.75)
        self.assertEqual(8, len(rules))

        a_rule = (frozenset(['b']), frozenset(['d']), 6, 0.75)
        self.assertTrue(a_rule in rules)

    def testSupport5(self):
        ts1 = perftesting.get_default_transactions()
        relim_input = itemmining.get_relim_input(ts1)
        report = itemmining.relim(relim_input, 5)
        rules = assocrules.mine_assoc_rules(report, min_support=5)
        self.assertEqual(2, len(rules))

        a_rule = (frozenset(['d']), frozenset(['b']), 6, 0.75)
        self.assertTrue(a_rule in rules)

    def testConfidenceForComplexRules(self):
        transab = (('a', 'b'), ) * 1000
        transac = (('a', 'c'), ) * 1000
        transabc = (('a', 'b', 'c'), ) * 5
        trans = transab + transac + transabc
        relim_input = itemmining.get_relim_input(trans)
        report = itemmining.relim(relim_input, 5)
        rules = assocrules.mine_assoc_rules(
            report, min_support=5, min_confidence=0.9)
        self.assertEqual(3, len(rules))

        a_rule = (frozenset(['b', 'c']), frozenset(['a']), 5, 1.0)
        self.assertTrue(a_rule in rules)
