from time import time
import random
import string
from pymining.itemmining import _fpgrowth, get_fptree, _relim,\
        get_relim_input, _sam, get_sam_input
from pymining.compat import range


def get_default_transactions():
    '''Returns a small list of transactions. For testing purpose.'''
    return (
            ('a', 'd'),
            ('a', 'c', 'd', 'e'),
            ('b', 'd'),
            ('b', 'c', 'd'),
            ('b', 'c'),
            ('a', 'b', 'd'),
            ('b', 'd', 'e'),
            ('b', 'c', 'd', 'e'),
            ('b', 'c'),
            ('a', 'b', 'd')
            )


def get_default_transactions_alt():
    '''Returns a small list of transactions. For testing purpose.'''
    return (
            ('a', 'b'),
            ('b', 'c', 'd'),
            ('a', 'c', 'd', 'e'),
            ('a', 'd', 'e'),
            ('a', 'b', 'c'),
            ('a', 'b', 'c', 'd'),
            ('a'),
            ('a', 'b', 'c'),
            ('a', 'b', 'd'),
            ('b', 'c', 'e'),
            )


def get_default_sequences():
    '''Returns a small list of sequences. For testing purpose.'''
    return ('caabc', 'abcb', 'cabc', 'abbca')


def get_random_transactions(
        transaction_number=500,
        max_item_per_transaction=100, max_key_length=50,
        key_alphabet=string.ascii_letters, universe_size=1000):
    '''Generates a random list of `transaction_number` transactions containing
       from 0 to `max_item_per_transaction` from a collection of
       `universe_size`. Each key has a maximum length of `max_key_length` and
       is computed from a sequence of characters specified by `key_alphabet`
       (default is ascii letters).

       If `key_alphabet` is None, range(universize_size) is used as the
       alphabet and `max_key_length` is ignored.
    '''

    if key_alphabet is None:
        words = list(range(universe_size))
    else:
        words = []
        for _ in range(universe_size):

            word = ''.join((
                random.choice(key_alphabet) for x in
                range(random.randint(1, max_key_length))))
            words.append(word)

    transactions = []
    for _ in range(transaction_number):
        transaction = {
            word for word in
            random.sample(words, random.randint(0, max_item_per_transaction))
        }
        transactions.append(transaction)

    return transactions


def test_sam(should_print=False, ts=None, support=2):
    if ts is None:
        ts = get_default_transactions()
    sam_input = get_sam_input(ts, lambda e: e)
    fis = set()
    report = {}
    n = _sam(sam_input, fis, report, support)
    if should_print:
        print(n)
        print(report)
    return (n, report)


def test_relim(should_print=False, ts=None, support=2):
    if ts is None:
        ts = get_default_transactions()
    relim_input = get_relim_input(ts, lambda e: e)
    fis = set()
    report = {}
    n = _relim(relim_input, fis, report, support)
    if should_print:
        print(n)
        print(report)
    return (n, report)


def test_fpgrowth(should_print=False, ts=None, support=2, pruning=False):
    if ts is None:
        ts = get_default_transactions()
    fptree = get_fptree(ts, lambda e: e, support)
    fis = set()
    report = {}
    n = _fpgrowth(fptree, fis, report, support, pruning)
    if should_print:
        print(n)
        print(report)
    return (n, report)


def test_itemset_perf(perf_round=10, sparse=True, seed=None):
    '''Non-scientifically tests the performance of three algorithms by running
       `perf_round` rounds of FP-Growth, FP-Growth without pruning, Relim, and
       SAM.

       A random set of transactions is created (the same is obviously used
       for all algorithms).

       If `sparse` is False, the random transactions are more dense, i.e., some
       elements appear in almost all transactions.

       The `seed` parameter can be used to obtain the same sample across
       multiple calls.
    '''
    random.seed(seed)

    if sparse:
        universe_size = 2000
        transaction_number = 500
        support = 10
    else:
        universe_size = 110
        transaction_number = 75
        support = 25
    transactions = get_random_transactions(
            transaction_number=transaction_number,
            universe_size=universe_size,
            key_alphabet=None)
    print('Random transactions generated with seed {0}\n'.format(seed))

    start = time()
    for i in range(perf_round):
        (n, report) = test_fpgrowth(
            False, transactions, support, pruning=True)
        print('Done round {0}'.format(i))
    end = time()
    print('FP-Growth (pruning on) took: {0}'.format(end - start))
    print('Computed {0} frequent item sets.'.format(n))

    start = time()
    for i in range(perf_round):
        (n, report) = test_fpgrowth(
            False, transactions, support, pruning=False)
        print('Done round {0}'.format(i))
    end = time()
    print('FP-Growth (pruning off) took: {0}'.format(end - start))
    print('Computed {0} frequent item sets.'.format(n))

    start = time()
    for i in range(perf_round):
        (n, report) = test_relim(False, transactions, support)
        print('Done round {0}'.format(i))
    end = time()
    print('Relim took: {0}'.format(end - start))
    print('Computed {0} frequent item sets.'.format(n))

    start = time()
    for i in range(perf_round):
        (n, report) = test_sam(False, transactions, support)
        print('Done round {0}'.format(i))
    end = time()
    print('Sam took: {0}'.format(end - start))
    print('Computed {0} frequent item sets.'.format(n))
