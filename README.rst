pymining - A collection of data mining algorithms in Python
===========================================================

:Authors:
  Barthelemy Dagenais
:Version: 0.1

pymining is a small collection of data mining algorithms implemented in Python.
I did not design any of the algorithms, but I use them in my own research so I
thought other developers might be interested to use them as well.

I started this small project because I could not find data mining algorithms
that were easily accessible in Python. Moreover, the libraries I am aware of
often include old algorithms that have been surpassed by newer ones.


Requirements
------------

pymining has been tested with Python 2.7 and 3.2.


Installation
------------

::

    pip install -e git://github.com/bartdag/pymining#egg=pymining


Usage
-----

**Frequent Item Set Mining**

::

    >>> from pymining import itemmining
    >>> transactions = (('a', 'b', 'c'), ('b'), ('a'), ('a', 'c', 'd'), ('b', 'c'), ('b', 'c'))
    >>> relim_input = itemmining.get_relim_input(transactions)
    >>> report = itemmining.relim(relim_input, min_support=2)
    >>> report
    set([(('c',), 4), (('b',), 4), (('a', 'c'), 2), (('a',), 3), (('c', 'b'), 3)])

    >>> # Test performance of multiple algorithms
    >>> itemmining.test_perf()
    Random transactions generated

    Done round 0
    Done round 1
    ...


Status of the project
---------------------

Three algorithms are currently implemented to find frequent item sets. Relim is
the recommended algorithm as it outperforms the two others (SaM and FP-growth)
in all of my benchmarks. This is probably due to my lazy implementation of
FP-growth.

The pruning option in FP-growth makes the algorithm slow and is turned to False by default for
now. This is surprising because pruning the tree should make it faster.


Todo
----

#. Write unit tests instead of manual testing (doh)
#. Move benchmark functions in a separate module
#. Implement at least one association rule mining algorithm


About performance and memory usage
----------------------------------

All algorithms are implemented in Python and not in a C extension. The library
does not require any dependency and can thus be installed in almost any Python
environment. 

The performance does increase with pypy and its jit. In one of my benchark,
FP-growth went from 100 seconds with cpython to 23 seconds with pypy and relim
went from 23 seconds to 4 seconds.

The memory consumption is quite high.


License
-------

This software is licensed under the `New BSD License`. See the `LICENSE` file
in the for the full license text.
