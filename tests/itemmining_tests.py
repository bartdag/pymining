import unittest
from pymining import itemmining, perftesting


class TestItemSetAlgo(unittest.TestCase):

    def test_relim(self):
        ts1 = perftesting.get_default_transactions()
        relim_input = itemmining.get_relim_input(ts1)
        report = itemmining.relim(relim_input, 2)
        self.assertEqual(17, len(report))
        self.assertEqual(6, report[frozenset(['b', 'd'])])

        ts2 = perftesting.get_default_transactions_alt()
        relim_input = itemmining.get_relim_input(ts2)
        report = itemmining.relim(relim_input, 2)
        self.assertEqual(19, len(report))
        self.assertEqual(5, report[frozenset(['a', 'b'])])

    def test_sam(self):
        ts1 = perftesting.get_default_transactions()
        sam_input = itemmining.get_sam_input(ts1)
        report = itemmining.sam(sam_input, 2)
        self.assertEqual(17, len(report))
        self.assertEqual(6, report[frozenset(['b', 'd'])])

        ts2 = perftesting.get_default_transactions_alt()
        sam_input = itemmining.get_sam_input(ts2)
        report = itemmining.sam(sam_input, 2)
        self.assertEqual(19, len(report))
        self.assertEqual(5, report[frozenset(['a', 'b'])])

    def test_fpgrowth_pruning_on(self):
        ts1 = perftesting.get_default_transactions()
        fp_input = itemmining.get_fptree(ts1)
        report = itemmining.fpgrowth(fp_input, 2, pruning=True)
        self.assertEqual(17, len(report))
        self.assertEqual(6, report[frozenset(['b', 'd'])])

        ts2 = perftesting.get_default_transactions_alt()
        fp_input = itemmining.get_fptree(ts2)
        report = itemmining.fpgrowth(fp_input, 2, pruning=True)
        self.assertEqual(19, len(report))
        self.assertEqual(5, report[frozenset(['a', 'b'])])

    def test_fpgrowth_pruning_off(self):
        ts1 = perftesting.get_default_transactions()
        fp_input = itemmining.get_fptree(ts1)
        report = itemmining.fpgrowth(fp_input, 2, pruning=False)
        self.assertEqual(17, len(report))
        self.assertEqual(6, report[frozenset(['b', 'd'])])

        ts2 = perftesting.get_default_transactions_alt()
        fp_input = itemmining.get_fptree(ts2)
        report = itemmining.fpgrowth(fp_input, 2, pruning=False)
        self.assertEqual(19, len(report))
        self.assertEqual(5, report[frozenset(['a', 'b'])])
