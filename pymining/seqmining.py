from collections import defaultdict


def freq_seq_enum(sequences, min_support):
    '''Enumerates all frequent sequences.

       :param sequences: A sequence of sequences.
       :param min_support: The minimal support of a set to be included.
       :rtype: A set of (frequent_sequence, support).
    '''
    freq_seqs = set()
    _freq_seq(sequences, tuple(), 0, min_support, freq_seqs)
    return freq_seqs


def _freq_seq(sdb, prefix, prefix_support, min_support, freq_seqs):
    if prefix:
        freq_seqs.add((prefix, prefix_support))
    locally_frequents = _local_freq_items(sdb, prefix, min_support)
    if not locally_frequents:
        return
    for (item, support) in locally_frequents:
        new_prefix = prefix + (item,)
        new_sdb = _project(sdb, new_prefix)
        _freq_seq(new_sdb, new_prefix, support, min_support, freq_seqs)


def _local_freq_items(sdb, prefix, min_support):
    items = defaultdict(int)
    freq_items = []
    for entry in sdb:
        visited = set()
        for element in entry:
            if element not in visited:
                items[element] += 1
                visited.add(element)
    # Sorted is optional. Just useful for debugging for now.
    for item in items:
        support = items[item]
        if support >= min_support:
            freq_items.append((item, support))
    return freq_items


def _project(sdb, prefix):
    new_sdb = []
    if not prefix:
        return sdb
    current_prefix_item = prefix[-1]
    for entry in sdb:
        j = 0
        projection = None
        for item in entry:
            if item == current_prefix_item:
                projection = entry[j + 1:]
                break
            j += 1
        if projection:
            new_sdb.append(projection)
    return new_sdb
