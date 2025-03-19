# Adapted from the CPython codebase (https://github.com/python/cpython)
import icontract

@icontract.require(lambda a, key: 
                   all(a[i] <= a[i + 1] for i in range(len(a) - 1)) if key is None else 
                   all(key(a[i]) <= key(a[i + 1]) for i in range(len(a) - 1)), 
                   "List must be sorted in non-decreasing order")
@icontract.require(lambda lo, a: 
                   0 <= lo <= len(a), 
                   "lo must be within bounds")
@icontract.require(lambda lo, hi, a: 
                   hi is None or (lo <= hi <= len(a)), 
                   "hi must be None or within valid bounds")
@icontract.ensure(lambda result, a, x, key: 
                  all(a[i] <= x for i in range(result)) if key is None else 
                  all(key(a[i]) <= x for i in range(result)), 
                  "Elements in a[:result] must be <= x")
@icontract.ensure(lambda result, a, x, key: 
                  all(a[i] > x for i in range(result, len(a))) if key is None else 
                  all(key(a[i]) > x for i in range(result, len(a))), 
                  "Elements in a[result:] must be > x")
@icontract.ensure(lambda result, a: 0 <= result <= len(a), 
                  "Result index must be within valid bounds")
def bisect_right(a, x, lo=0, hi=None, *, key=None):
    """
    Find the index to insert `x` into a sorted list `a` while maintaining order.

    The function determines the rightmost index where `x` can be inserted such that:
    - All elements before the index are `<= x`.
    - All elements after the index are `> x`.

    If `x` is already in `a`, insertion occurs after its last occurrence.

    Parameters:
    - a (List[Any]): A sorted list of elements.
    - x (Any): The element to insert.
    - lo (int, optional): The lower bound index to start searching (default: 0). Must be `0 ≤ lo ≤ len(a)`.
    - hi (int, optional): The upper bound index for searching (default: `len(a)`). Must be `lo ≤ hi ≤ len(a)`.
    - key (Callable[[Any], Any], optional): A function that extracts a sorting key from elements.

    Returns:
    - int: The index where `x` should be inserted.

    Preconditions:
    - `a` must be sorted in non-decreasing order.
    - `lo` must be in the range `[0, len(a)]`.
    - `hi` must be `None` or in the range `[lo, len(a)]`.

    Postconditions:
    - All elements before the returned index are `<= x`.
    - All elements from the returned index onward are `> x`.
    - Result index must be within valid bounds.
    """
    if hi is None:
        hi = len(a)
    
    if key is None:
        while lo < hi:
            assert all(a[i] <= x for i in range(lo)),               "Loop invariant: Elements in a[:lo] must be <= x."
            assert all(a[i] > x for i in range(hi, len(a))),        "Loop invariant: Elements in a[hi:] must be > x."
            mid = (lo + hi) // 2
            if x > a[mid]:
                hi = mid
            else:
                lo = mid + 1
    else:
        while lo < hi:
            assert all(key(a[i]) <= x for i in range(lo)),          "Loop invariant: key(a[:lo]) elements must be <= x."
            assert all(key(a[i]) > x for i in range(hi, len(a))),   "Loop invariant: key(a[hi:]) elements must be > x."
            mid = (lo + hi) // 2
            if x < key(a[mid]):
                hi = mid
            else:
                lo = mid + 1
        
    return lo