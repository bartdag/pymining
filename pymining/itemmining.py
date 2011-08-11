from collections import defaultdict, deque
import string
from time import time
import random
import sys


if sys.version_info[0] < 3:
    range = xrange


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


def get_random_transactions(transaction_number=250,
        max_item_per_transaction=100, max_key_length=50,
        key_alphabet=None, universe_size = 1000):
    '''Generates a random list of `transaction_number` transactions containing
       from 0 to `max_item_per_transaction` from a collection of
       `universe_size`. Each key has a maximum length of `max_key_length` and
       is computed from a sequence of characters specified by `key_alphabet`
       (default is ascii letters).
    '''
    
    if key_alphabet is None:
        key_alphabet = string.ascii_letters

    words = []
    for _ in range(universe_size): 

        word = ''.join((random.choice(key_alphabet) for x in
            range(random.randint(1, max_key_length))))
        words.append(word)

    transactions = []
    for _ in range(transaction_number):
        transaction = {word for word in random.sample(words, random.randint(0,
            max_item_per_transaction))}
        transactions.append(transaction)

    return transactions


def compare(t1, t2):
    '''Returns r < 1 if t1 < t2, r > 1 if t2 > t1, and r == 0 if t1 == t2'''
    c1= t1.current_pos
    c2 = t2.current_pos
    s1 = t1.inner_len()
    s2 = t2.inner_len()
    while c1 < s1 and c2 < s2:
        v1 = t1.seq[c1]
        v2 = t2.seq[c2]
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        c1 += 1
        c2 += 1

    return len(t1) - len(t2)


def _sort_transactions_by_freq(transactions, key_func):
    key_seqs = [[key_func(i) for i in sequence] for sequence in transactions]
    frequencies = get_frequencies(key_seqs)

    asorted_seqs = []
    for key_seq in key_seqs:
        if len(key_seq) == 0:
            continue
        # Sort each transaction (infrequent key first)
        l = [(frequencies[i], i) for i in key_seq]
        l.sort()
        asorted_seqs.append(tuple(l))
    # Sort all transactions. Those with infrequent key first, first
    asorted_seqs.sort()

    return asorted_seqs

def get_frequencies(transactions):
    '''Computes a dictionary, {key:frequencies} containing the frequency of
       each key in all transactions. Duplicate keys in a transaction are
       counted twice.

       :param transactions: a sequence of sequences. [ [transaction items...]]
    '''
    frequencies = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            frequencies[item] += 1
    return frequencies


def get_sam_input(transactions, key_func):
    '''Given a list of transactions and a key function, returns a data
       structure used as the input of the sam algorithm.

       :param transactions: a sequence of sequences. [ [transaction items...]]
       :param key_func: a function that returns a comparable key for a
        transaction item.
    '''
    asorted_seqs = _sort_transactions_by_freq(transactions, key_func)

    # Group same transactions together
    sam_input = deque()
    visited = {}
    current = 0
    for seq in asorted_seqs:
        if seq not in visited:
            sam_input.append((1, seq))
            visited[seq] = current
            current += 1
        else:
            i = visited[seq]
            (count, oldseq) = sam_input[i]
            sam_input[i] = (count + 1, oldseq)
    return sam_input


def sam(sam_input, fis, report, min_support):
    '''Finds frequent item sets of items appearing in a list of transactions based
       on the Split and Merge algorithm by Christian Borgelt.

       :sam_input: The input of the algorithm. Must come from `get_sam_input`.
       :fis: An empty set used to temporarily stored the frequent item sets.
       :report: A set that will contain the mined frequent item sets. Each set
        in `report` contains tuples of (total freq. of item, key of item).
       :min_support: The minimal support of a set to be included in `report`.
    '''
    n = 0
    a = deque(sam_input)
    while len(a) > 0 and len(a[0][1]) > 0:
        b = deque()
        s = 0
        i = a[0][1][0]
        while len(a) > 0 and len(a[0][1]) > 0 and a[0][1][0] == i:
            s = s + a[0][0]
            a[0] = (a[0][0], a[0][1][1:])
            if len(a[0][1]) > 0:
                b.append(a.popleft())
            else:
                a.popleft()
        c = deque(b)
        d = deque()
        while len(a) > 0 and len(b) > 0:
            if a[0][1] > b[0][1]:
                d.append(b.popleft())
            elif a[0][1] < b[0][1]:
                d.append(a.popleft())
            else:
                b[0] = (b[0][0] + a[0][0], b[0][1])
                d.append(b.popleft())
                a.popleft()
        while len(a) > 0:
            d.append(a.popleft())
        while len(b) > 0:
            d.append(b.popleft())
        a = d
        if s >= min_support:
            fis.add(i)
            report.add((frozenset(fis), s))
            #print('{0} with support {1}'.format(fis, s))
            n = n + 1 + sam(c, fis, report, min_support)
            fis.remove(i)
    return n


def test_sam(should_print=False, ts=None, support=2):
    if ts is None:
        ts = get_default_transactions()
    sam_input = get_sam_input(ts, lambda e: e)
    fis = set()
    report = set()
    n = sam(sam_input, fis, report, support)
    if should_print:
        print(n)
        print(report)
    return (n, report)


def get_relim_input(transactions, key_func):
    '''Given a list of transactions and a key function, returns a data
       structure used as the input of the relim algorithm.

       :param transactions: a sequence of sequences. [ [transaction items...]]
       :param key_func: a function that returns a comparable key for a
        transaction item.
    '''
    asorted_seqs = _sort_transactions_by_freq(transactions, key_func)
    relim_input = []
    for seq in asorted_seqs:
        if len(seq) < 2:
            continue
        if len(relim_input) > 0 and relim_input[-1][0][1] == seq[0]:
            ((count, char), lists) = relim_input[-1]
            rest = seq[1:]
            found = False
            for i, (rest_count, rest_seq) in enumerate(lists):
                if rest_seq == rest:
                    lists[i] = (rest_count + 1, rest_seq)
                    found = True
                    break
            if not found:
                lists.append((1, rest))
            relim_input[-1] = ((count + 1, char), lists)
        else:
            relim_input.append(((1, seq[0]), [(1, seq[1:])] ))
        # Take first tuple
        # If firm tuple == current, just add to the list.
        #    If last == current, just increment counter.
        #    # Ohterwise, just add a new one.
        # Otherwise, create a new one.
    return deque(reversed(relim_input))


def testperf(perf_round=10):

    transactions = get_random_transactions()
    print('Random transactions generated\n')
    #print(transactions)
    #print()

    start = time()
    for i in range(perf_round):
        (n, report) = test_sam(False, transactions, 10)
        print('Done round {0}'.format(i))
    end = time()
    print('Sam took: {0}'.format(end-start))
    print('Computed {0} frequent item sets.'.format(n))
    #print(report)
