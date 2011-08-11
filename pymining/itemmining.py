from collections import defaultdict, deque, OrderedDict
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

    return (asorted_seqs, frequencies)

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
    (asorted_seqs, _) = _sort_transactions_by_freq(transactions, key_func)

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


def _new_relim_input(size, key_map):
    i = 0
    l = []
    for key in key_map:
        if i >= size:
            break
        l.append(((0, key), []))
    return l


def _get_key_map(frequencies):
    l = [(frequencies[k], k) for k in frequencies]
    l.sort(reverse=True)
    key_map = OrderedDict()
    for i, v in enumerate(l):
        key_map[v] = i
    return key_map


def get_relim_input(transactions, key_func):
    '''Given a list of transactions and a key function, returns a data
       structure used as the input of the relim algorithm.

       :param transactions: a sequence of sequences. [ [transaction items...]]
       :param key_func: a function that returns a comparable key for a
        transaction item.
    '''

    # Data Structure
    # relim_input[x][0] = (count, key_freq)
    # relim_input[x][1] = [(count, (key_freq, )]
    #
    # in other words:
    # relim_input[x][0][0] = count of trans with prefix key_freq
    # relim_input[x][0][1] = prefix key_freq
    # relim_input[x][1] = lists of transaction rests
    # relim_input[x][1][x][0] = number of times a rest of transaction appears
    # relim_input[x][1][x][1] = rest of transaction prefixed by key_freq

    (asorted_seqs, frequencies) = _sort_transactions_by_freq(transactions, key_func)
    key_map = _get_key_map(frequencies)

    relim_input = _new_relim_input(len(key_map), key_map)
    for seq in asorted_seqs:
        if len(seq) < 2:
            continue
        index = key_map[seq[0]]
        ((count, char), lists) = relim_input[index]
        rest = seq[1:]
        found = False
        for i, (rest_count, rest_seq) in enumerate(lists):
            if rest_seq == rest:
                lists[i] = (rest_count + 1, rest_seq)
                found = True
                break
        if not found:
            lists.append((1, rest))
        relim_input[index] = ((count + 1, char), lists)
    return (relim_input, key_map)


def relim(rinput, fis, report, min_support):
    (relim_input, key_map) = rinput
    n = 0
    # Maybe this one isn't necessary
    a = deque(relim_input)
    while len(a) > 0:
        item = a[-1][0][1]
        s = item[0]
        if s >= min_support:
            fis.add(item)
            print('Report {0} with support {1}'.format(fis, s))
            report.add((frozenset(fis), s))
            b = _new_relim_input(len(a) - 1, key_map)
            rest_lists = a[-1][1]

            for (count, rest) in rest_lists:
                k = rest[0]
                index = key_map[k]
                new_rest = rest[1:]
                # Only add this rest if it's not empty!
                ((k_count, k), lists) = b[index]
                if len(new_rest) > 0:
                    lists.append((count, new_rest))
                b[index] = ((k_count + count, k), lists)
            n = n + 1 + relim((b, key_map), fis, report, min_support)
            fis.remove(item)
        
        rest_lists = a[-1][1]
        for (count, rest) in rest_lists:
            k = rest[0]
            index = key_map[k]
            new_rest = rest[1:]
            ((k_count, k), lists) = a[index]
            if len(new_rest) > 0:
                lists.append((count, new_rest))
            a[index] = ((k_count + count, k), lists)
        a.pop()
    return n


def test_relim(should_print=False, ts=None, support=2):
    if ts is None:
        ts = get_default_transactions()
    relim_input = get_relim_input(ts, lambda e: e)
    fis = set()
    report = set()
    n = relim(relim_input, fis, report, support)
    if should_print:
        print(n)
        print(report)
    return (n, report)


def test_perf(perf_round=10):

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
