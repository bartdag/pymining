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

def get_default_transactions_alt():
    '''Returns a small list of transactions. For testing purpose.'''
    return (
            ('a', 'b'),
            ('b', 'c', 'd'),
            ('a','c', 'd', 'e'),
            ('a', 'd', 'e'),
            ('a', 'b', 'c'),
            ('a', 'b', 'c', 'd'),
            ('a'),
            ('a', 'b', 'c'),
            ('a', 'b', 'd'),
            ('b', 'c', 'e'),
            )


def get_random_transactions(transaction_number=500,
        max_item_per_transaction=100, max_key_length=50,
        key_alphabet=None, universe_size=1000):
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


def _sort_transactions_by_freq(transactions, key_func, reverse_int=False,
        reverse_ext=False, sort_ext=True):
    key_seqs = [{key_func(i) for i in sequence} for sequence in transactions]
    frequencies = get_frequencies(key_seqs)

    asorted_seqs = []
    for key_seq in key_seqs:
        if len(key_seq) == 0:
            continue
        # Sort each transaction (infrequent key first)
        l = [(frequencies[i], i) for i in key_seq]
        l.sort(reverse=reverse_int)
        asorted_seqs.append(tuple(l))
    # Sort all transactions. Those with infrequent key first, first
    if sort_ext:
        asorted_seqs.sort(reverse=reverse_ext)

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
    '''Finds frequent item sets of items appearing in a list of transactions
       based on the Split and Merge algorithm by Christian Borgelt.

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
            fis.add(i[1])
            report.add((frozenset(fis), s))
            #print('{0} with support {1}'.format(fis, s))
            n = n + 1 + sam(c, fis, report, min_support)
            fis.remove(i[1])
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
        i = i + 1
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

    (asorted_seqs, frequencies) = _sort_transactions_by_freq(transactions,
            key_func)
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
    '''Finds frequent item sets of items appearing in a list of transactions
       based on Recursive Elimination algorithm by Christian Borgelt.

       :rinput: The input of the algorithm. Must come from
        `get_relim_input`.
       :fis: An empty set used to temporarily stored the frequent item sets.
       :report: A set that will contain the mined frequent item sets. Each set
        in `report` contains tuples of (total freq. of item, key of item).
       :min_support: The minimal support of a set to be included in `report`.
    '''
    (relim_input, key_map) = rinput
    n = 0
    # Maybe this one isn't necessary
    #a = deque(relim_input)
    a = relim_input
    while len(a) > 0:
        item = a[-1][0][1]
        s = a[-1][0][0]
        if s >= min_support:
            fis.add(item[1])
            #print('Report {0} with support {1}'.format(fis, s))
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
            fis.remove(item[1])

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


class FPNode(object):

    def __init__(self, key, parent):
        self.children = {}
        self.parent = parent
        self.key = key
        self.count = 0
        self.next_node = None

    def add_path(self, path, index, length, heads, last_insert):
        if index >= length:
            return

        child_key = path[index]
        index += 1

        try:
            child = self.children[child_key]
        except Exception:
            child = self._create_child(child_key, heads, last_insert)
        child.count += 1
        heads[child_key][1] += 1

        child.add_path(path, index, length, heads, last_insert)

    def _create_child(self, child_key, heads, last_insert):
        child = FPNode(child_key, self)
        self.children[child_key] = child
        try:
            last_child = last_insert[child_key]
            last_child.next_node = child
        except Exception:
            heads[child_key] = [child, 0]
        last_insert[child_key] = child

        return child

    def get_cond_tree(self, child, count, visited, heads, last_insert,
            dont_create=False):

        key = self.key

        if dont_create:
            # This is a head, we don't want to copy it.
            cond_node = None
        else:
            try:
                cond_node = visited[self]
            except Exception:
                cond_node = self._create_cond_child(visited, heads,
                        last_insert)

        if child is not None:
            # We came from a cond node. Maintain children
            cond_node.children[child.key] = child

        if self.parent is not None:
            # Recursion
            parent_node = self.parent.get_cond_tree(cond_node, count, visited,
                    heads, last_insert)
            if cond_node is not None:
                cond_node.count += count
                heads[key][1] += count
                cond_node.parent = parent_node

        return cond_node

    def _create_cond_child(self, visited, heads, last_insert):
        key = self.key
        cond_node = FPNode(key, None) 
        visited[self] = cond_node
        try:
            last_cond_node = last_insert[key]
            last_cond_node.next_node = cond_node
        except Exception:
            # Don't add root!
            if self.parent is not None:
                heads[key] = [cond_node, 0]
        last_insert[key] = cond_node

        return cond_node

    def prune_me(self):
        parent = self.parent
        del(parent.children[self.key])
        for child_key in self.children:
            child = self.children[child_key]
            if child_key in parent.children:
                # Combine same children
                parent.children[child_key].count += child.count
            else:
                # Add new child
                child.parent = parent
                parent.children[child_key] = child

    def __str__(self):
        child_str = ','.join([str(key) for key in self.children])
        return '{0} ({1})  [{2}]  {3}'.format(self.key, self.count, child_str,
                self.next_node is not None)

    def __repr__(self):
        return self.__str__()
    

def get_fptree(transactions, key_func, min_support=2):
    asorted_seqs, frequencies = _sort_transactions_by_freq(transactions, key_func, True,
            False, False)
    transactions = [[item[1] for item in aseq if item[0] >= min_support] for
            aseq in asorted_seqs]

    root = FPNode(None, None)
    heads = {}
    last_insert = {}
    for transaction in transactions:
        root.add_path(transaction, 0, len(transaction), heads, last_insert)
                
    #new_heads = sorted(heads.values(), key=lambda v: (v[1], v[0].key))
    #new_heads = tuple(heads.values())

    return (root, heads)


def _print_prefix_tree(node):
    print(node)
    for key in sorted(node.children):
        _print_prefix_tree(node.children[key])


def _print_head(head):
    node = head
    while node is not None:
        print(node)
        node = node.parent


def _create_cond_tree(head_node):
    visited = {}
    new_heads = {}
    last_insert = {}
    while head_node is not None:
        head_node.get_cond_tree(None, head_node.count, visited, new_heads,
                last_insert, True)
        head_node = head_node.next_node
    return new_heads


def _prune_cond_tree(new_heads, min_support):
    for (node, head_support) in new_heads.values():
        if head_support < min_support:
            while node is not None:
                node.prune_me()
                node = node.next_node
            # First, you cannot delete while iterating in a dict.
            # Second, deleting afterwards takes longer than skipping it
            # in fpgrowth's loopme
            #del(new_heads[key])


def fpgrowth(fptree, fis, report, min_support=2):
    (_, heads) = fptree
    n = 0
    for (head_node, head_support) in heads.values():
        if head_support < min_support:
            continue

        fis.add(head_node.key)
        #print('Report {0} with support {1}'.format(fis, head_support))
        report.add((frozenset(fis), head_support))
        new_heads = _create_cond_tree(head_node)
        _prune_cond_tree(new_heads, min_support)
        n = n + 1 + fpgrowth((None, new_heads), fis, report, min_support)
        fis.remove(head_node.key)
    return n


def test_perf(perf_round=10, sparse=True):

    if sparse:
        universe_size = 2000
        transaction_number = 500
    else:
        universe_size = 200
        transaction_number = 100
    transactions = get_random_transactions(
            transaction_number=transaction_number,
            universe_size=universe_size)
    print('Random transactions generated\n')
    #print(transactions)
    #print()

    start = time()
    for i in range(perf_round):
        (n, report) = test_relim(False, transactions, 10)
        print('Done round {0}'.format(i))
    end = time()
    print('Relim took: {0}'.format(end - start))
    print('Computed {0} frequent item sets.'.format(n))
    #print(report)

    start = time()
    for i in range(perf_round):
        (n, report) = test_sam(False, transactions, 10)
        print('Done round {0}'.format(i))
    end = time()
    print('Sam took: {0}'.format(end - start))
    print('Computed {0} frequent item sets.'.format(n))
