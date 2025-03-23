# Adapted from the SymPy repository (https://github.com/sympy/sympy)

from enum import Enum
from sympy.core.containers import Tuple
from sympy.core.numbers import (Integer, Rational)
from sympy.core.singleton import S
import sympy.polys
import icontract

from math import gcd

class EgyptianAlgorithm(Enum):
    GREEDY = 1
    GRAHAM_JEWETT = 2
    TAKENOUCHI = 3
    GOLOMB = 4

def crosshair_ignore(func):
    func.__crosshair_ignore__ = True
    return func


@icontract.require(
    lambda numerator, denominator: numerator > 0 and denominator > 0,
    "The input rational number must be strictly positive"
)
@icontract.require(
    lambda numerator, denominator: numerator <= 10 and denominator <= 10,
    "Numerator must be ≤ 10 and denominator ≤ 10 to prevent excessive computation"
)
@icontract.ensure(
    lambda result, numerator, denominator: sum(Rational(1, d) for d in result) == Rational(numerator, denominator),
    "The sum of the reciprocals of the returned denominators must equal the input rational number"
)
@icontract.ensure(
    lambda result: all(isinstance(d, Integer) and d > 0 for d in result),
    "All denominators must be positive integers"
)
def egyptian_fraction(numerator: int, denominator: int, algorithm: EgyptianAlgorithm = EgyptianAlgorithm.GREEDY):
    """
    Return the list of denominators of an Egyptian fraction
    expansion [1]_ of the said rational `r`.

    Parameters
    ==========

    r : Rational or (p, q)
        a positive rational number, ``p/q``.
    algorithm : { "Greedy", "Graham Jewett", "Takenouchi", "Golomb" }, optional
        Denotes the algorithm to be used (the default is "Greedy").

    Examples
    ========

    >>> from sympy import Rational
    >>> from sympy.ntheory.egyptian_fraction import egyptian_fraction
    >>> egyptian_fraction(Rational(3, 7))
    [3, 11, 231]
    >>> egyptian_fraction((3, 7), "Graham Jewett")
    [7, 8, 9, 56, 57, 72, 3192]
    >>> egyptian_fraction((3, 7), "Takenouchi")
    [4, 7, 28]
    >>> egyptian_fraction((3, 7), "Golomb")
    [3, 15, 35]
    >>> egyptian_fraction((11, 5), "Golomb")
    [1, 2, 3, 4, 9, 234, 1118, 2580]

    See Also
    ========

    sympy.core.numbers.Rational

    Notes
    =====

    Currently the following algorithms are supported:

    1) Greedy Algorithm

       Also called the Fibonacci-Sylvester algorithm [2]_.
       At each step, extract the largest unit fraction less
       than the target and replace the target with the remainder.

       It has some distinct properties:

       a) Given `p/q` in lowest terms, generates an expansion of maximum
          length `p`. Even as the numerators get large, the number of
          terms is seldom more than a handful.

       b) Uses minimal memory.

       c) The terms can blow up (standard examples of this are 5/121 and
          31/311).  The denominator is at most squared at each step
          (doubly-exponential growth) and typically exhibits
          singly-exponential growth.

    2) Graham Jewett Algorithm

       The algorithm suggested by the result of Graham and Jewett.
       Note that this has a tendency to blow up: the length of the
       resulting expansion is always ``2**(x/gcd(x, y)) - 1``.  See [3]_.

    3) Takenouchi Algorithm

       The algorithm suggested by Takenouchi (1921).
       Differs from the Graham-Jewett algorithm only in the handling
       of duplicates.  See [3]_.

    4) Golomb's Algorithm

       A method given by Golumb (1962), using modular arithmetic and
       inverses.  It yields the same results as a method using continued
       fractions proposed by Bleicher (1972).  See [4]_.

    If the given rational is greater than or equal to 1, a greedy algorithm
    of summing the harmonic sequence 1/1 + 1/2 + 1/3 + ... is used, taking
    all the unit fractions of this sequence until adding one more would be
    greater than the given number.  This list of denominators is prefixed
    to the result from the requested algorithm used on the remainder.  For
    example, if r is 8/3, using the Greedy algorithm, we get [1, 2, 3, 4,
    5, 6, 7, 14, 420], where the beginning of the sequence, [1, 2, 3, 4, 5,
    6, 7] is part of the harmonic sequence summing to 363/140, leaving a
    remainder of 31/420, which yields [14, 420] by the Greedy algorithm.
    The result of egyptian_fraction(Rational(8, 3), "Golomb") is [1, 2, 3,
    4, 5, 6, 7, 14, 574, 2788, 6460, 11590, 33062, 113820], and so on.

    References
    ==========

    .. [1] https://en.wikipedia.org/wiki/Egyptian_fraction
    .. [2] https://en.wikipedia.org/wiki/Greedy_algorithm_for_Egyptian_fractions
    .. [3] https://www.ics.uci.edu/~eppstein/numth/egypt/conflict.html
    .. [4] https://web.archive.org/web/20180413004012/https://ami.ektf.hu/uploads/papers/finalpdf/AMI_42_from129to134.pdf

    """
    r = Rational(numerator, denominator)

    # Common cases that all methods agree on
    x, y = r.as_numer_denom()
    if y == 1 and x == 2:
        return [Integer(i) for i in [1, 2, 3, 6]]
    if x == y + 1:
        return [S.One, y]

    prefix, rem = egypt_harmonic(r)
    if rem == 0:
        return prefix
    # Work in Python ints
    x, y = rem.p, rem.q

    if algorithm == EgyptianAlgorithm.GREEDY:
        postfix = egypt_greedy(x, y)
    elif algorithm == EgyptianAlgorithm.GRAHAM_JEWETT:
        postfix = egypt_graham_jewett(x, y)
    elif algorithm == EgyptianAlgorithm.TAKENOUCHI:
        postfix = egypt_takenouchi(x, y)
    elif algorithm == EgyptianAlgorithm.GOLOMB:
        postfix = egypt_golomb(x, y)
    return prefix + [Integer(i) for i in postfix]


@icontract.require(
    lambda x: isinstance(x, int) and x > 0,
    "x must be a positive integer"
)
@icontract.require(
    lambda y: isinstance(y, int) and y > 0,
    "y must be a positive integer"
)
@icontract.require(
    lambda x, y: gcd(x, y) == 1,
    "gcd(x, y) must be 1"
)
@icontract.require(
    lambda x, y: x == 1 or x < y,
    "For non-unit fraction, x must be less than y"
)
@icontract.ensure(
    lambda result, x, y: sum(Rational(1, d) for d in result) == Rational(x, y),
    "The sum of reciprocals must equal x/y"
)
@icontract.ensure(
    lambda result: all(isinstance(d, int) and d > 0 for d in result),
    "All denominators must be positive integers"
)
def egypt_greedy(x, y):
    if x == 1:
        return [y]
    else:
        a = (-y) % x
        b = y*(y//x + 1)
        c = gcd(a, b)
        if c > 1:
            num, denom = a//c, b//c
        else:
            num, denom = a, b
        return [y//x + 1] + egypt_greedy(num, denom)


@icontract.require(
    lambda x: isinstance(x, int) and x > 0,
    "x must be a positive integer"
)
@icontract.require(
    lambda y: isinstance(y, int) and y > 0,
    "y must be a positive integer"
)
@icontract.require(
    lambda x, y: gcd(x, y) == 1,
    "gcd(x, y) must be 1"
)
@icontract.require(
    lambda x, y: x == 1 or x < y,
    "For non-unit fraction, x must be less than y"
)
@icontract.ensure(
    lambda result, x, y: sum(Rational(1, d) for d in result) == Rational(x, y),
    "The sum of reciprocals must equal x/y"
)
@icontract.ensure(
    lambda result: all(isinstance(d, int) and d > 0 for d in result),
    "All denominators must be positive integers"
)
def egypt_graham_jewett(x, y):
    l = [y] * x

    # l is now a list of integers whose reciprocals sum to x/y.
    # we shall now proceed to manipulate the elements of l without
    # changing the reciprocated sum until all elements are unique.

    while len(l) != len(set(l)):
        assert sum(Rational(1, d) for d in l) == Rational(x, y), "Loop invariant: sum(1/d for d in l) == x/y"
        l.sort()  # so the list has duplicates. find a smallest pair
        for i in range(len(l) - 1):
            if l[i] == l[i + 1]:
                break
        # we have now identified a pair of identical
        # elements: l[i] and l[i + 1].
        # now comes the application of the result of graham and jewett:
        l[i + 1] = l[i] + 1
        # and we just iterate that until the list has no duplicates.
        l.append(l[i]*(l[i] + 1))
    return sorted(l)


@icontract.require(
    lambda x: isinstance(x, int) and x > 0,
    "x must be a positive integer"
)
@icontract.require(
    lambda y: isinstance(y, int) and y > 0,
    "y must be a positive integer"
)
@icontract.require(
    lambda x, y: gcd(x, y) == 1,
    "gcd(x, y) must be 1"
)
@icontract.require(
    lambda x, y: x == 1 or x < y,
    "For non-unit fraction, x must be less than y"
)
@icontract.ensure(
    lambda result, x, y: sum(Rational(1, d) for d in result) == Rational(x, y),
    "The sum of reciprocals must equal x/y"
)
@icontract.ensure(
    lambda result: all(isinstance(d, int) and d > 0 for d in result),
    "All denominators must be positive integers"
)
def egypt_takenouchi(x, y):
    # Special cases for 3/y
    if x == 3:
        if y % 2 == 0:
            return [y//2, y]
        i = (y - 1)//2
        j = i + 1
        k = j + i
        return [j, k, j*k]
    l = [y] * x

    while len(l) != len(set(l)):
        assert sum(Rational(1, d) for d in l) == Rational(x, y), "Loop invariant: sum(1/d for d in l) == x/y"
        l.sort()
        for i in range(len(l) - 1):
            if l[i] == l[i + 1]:
                break
        k = l[i]
        if k % 2 == 0:
            l[i] = l[i] // 2
            del l[i + 1]
        else:
            l[i], l[i + 1] = (k + 1)//2, k*(k + 1)//2
    return sorted(l)


@icontract.require(
    lambda x: isinstance(x, int) and x > 0,
    "x must be a positive integer"
)
@icontract.require(
    lambda y: isinstance(y, int) and y > 0,
    "y must be a positive integer"
)
@icontract.require(
    lambda x, y: gcd(x, y) == 1,
    "gcd(x, y) must be 1"
)
@icontract.require(
    lambda x, y: x < y,
    "x must be less than y for egypt_golomb"
)
@icontract.ensure(
    lambda result, x, y: sum(Rational(1, d) for d in result) == Rational(x, y),
    "The sum of reciprocals must equal x/y"
)
@icontract.ensure(
    lambda result: all(isinstance(d, int) and d > 0 for d in result),
    "All denominators must be positive integers"
)
def egypt_golomb(x, y):
    if x == 1:
        return [y]
    xp = sympy.polys.ZZ.invert(int(x), int(y))
    rv = [xp*y]
    rv.extend(egypt_golomb((x*xp - 1)//y, xp))
    return sorted(rv)


@crosshair_ignore
def egypt_harmonic(r):
    rv = []
    d = S.One
    acc = S.Zero
    while acc + 1/d <= r:
        acc += 1/d
        rv.append(d)
        d += 1
    return (rv, r - acc)