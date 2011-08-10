from collections import defaultdict
from collections import deque


def get_default_transactions():
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


def get_frequencies(transactions):
    frequencies = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            frequencies[item] += 1
    return frequencies


def get_sorted_transactions(transactions, frequencies):
    return [
            sorted(transaction, key=lambda e: frequencies[e]) for transaction
            in transactions]


def get_asorted_transactions(transactions, frequencies):
    return sorted(transactions, key=lambda t: lexi_repr(t, frequencies))


def get_sam_data(transactions):
    sam_data = deque()
    visited = {}
    current = 0
    for transaction in transactions:
        key = str(transaction)
        if key not in visited:
            sam_data.append((1, transaction))
            visited[key] = current
            current += 1
        else:
            # This cannot be a list... sorry!
            # TODO CHANGE all internal lists for tuples... sorry
            (count, transaction) = sam_data[visited[key]]
            sam_data[visited[key]] = (count + 1, transaction)

    return sam_data


def transform(transactions):
    frequencies = get_frequencies(transactions)
    sorted_transactions = get_sorted_transactions(transactions, frequencies)
    asorted_transactions = get_asorted_transactions(sorted_transactions,
            frequencies)
    sam_data = get_sam_data(asorted_transactions)
    return (sam_data, frequencies)


def lexi_repr(transaction, frequencies):
    return [(frequencies[i], i) for i in transaction]

# ALMOST, but ad should be four
# cd is reported twice with different values
# b and d are wrong.
# again, look at the return value (debug -1)
def sam(sam_data, fis, min_support, frequencies):
    #print('Debug -1: sam_data={0}, fis={1}'.format(sam_data, fis))
    n = 0
    # Will contain everything, but some transactions will be pruned from their
    # prefix.
    a = deque(sam_data)
    while len(a) > 0 and len(a[0][1]) > 0:
        #print('DEBUG 0: a={0}'.format(a))
        # contains the prefix
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
        #print('DEBUG 1: a={0}, b={1}'.format(a,b))
        # Is this a clone OR a pointer...
        # contains the prefix
        c = deque(b)
        d = deque() # could reuse a, because it erase it... but what about b...
        while len(a) > 0 and len(b) > 0:
            lexi_a = lexi_repr(a[0][1], frequencies)
            lexi_b = lexi_repr(b[0][1], frequencies)
            if lexi_a > lexi_b:
                #print('a > b a={0}, b={1}'.format(lexi_a, lexi_b))
                d.append(b.popleft())
            elif lexi_a < lexi_b:
                #print('a < b a={0}, b={1}'.format(lexi_a, lexi_b))
                d.append(a.popleft())
            else:
                #print('a == b a={0}, b={1}'.format(lexi_a, lexi_b))
                b[0] = (b[0][0] + a[0][0], b[0][1])
                d.append(b.popleft())
                a.popleft()
        #print('DEBUG 3:\n a={0}\n b={1}\n d={2}'.format(a,b,d))
        while len(a) > 0:
            d.append(a.popleft())
        while len(b) > 0:
            d.append(b.popleft())
        #print('DEBUG 4:\n a={0}\n b={1}\n c={2}\n d={3}'.format(a, b, c, d))
        a = deque(d)
        if s >= min_support:
            fis.add(i)
            print('{0} with support {1}'.format(fis, s))
            n = n + 1 + sam(c, fis, min_support, frequencies)
            fis.remove(i)
        #print('LOOPING with a={0}'.format(a))

    return n

def test_sam():
    ts = get_default_transactions()
    sam_data, frequencies = transform(ts)
    fis = set()
    return sam(sam_data, fis, 2, frequencies)








def relim(transactions, items, s=2):
    current = []
    t_list1 = t_list2 = None
    n = 0
    while len(transactions) > 0:
        i = len(transactions) - 1
        pass

