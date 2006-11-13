# (C) Numbler Llc 2006
# See License For Details.

#
# Handy nested list flattener
#

# Danny Yoo has given a mind-blowing continuation implementation that
# will not overflow the stack. Below goes a recursive-iterator
# implementation.  To avoid deep recursion the code can simluate its
# own stack (or hope that Python gains tail-call optimization *grin*)
# but for simplicity's sake we just use recursion.
#

# FIXME: there has to be a faster test for iterability... look for a "__iter__" in dir?
def _isIterable(iterable):
     """Test for iterable-ness."""
     try:
          iter(iterable)
     except TypeError:
          return False
     return True

def _isBadIterable(iterable):
     """Return True if it's a 'bad' iterable.

     Note: string's are bad because, when iterated they return strings
           making itterflatten loop infinitely.
     """
     return isinstance(iterable, basestring)

# flaws: too many fn calls
#        checks every item twice for iterability
# 
# def flatten(iterable):
#     """Return a flattened iterator."""
#     # sanity check: have we been given an iterable?  if not just yield it
#     if not _isIterable(iterable):
#          yield iterable
#          return
#     it = iter(iterable)
#     for e in it:
#         if _isIterable(e) and not _isBadIterable(e):
#             # Recurse into iterators.
#             for f in flatten(e):
#                 yield f
#         else:
#             yield e

def isiterable(iterable):
    return hasattr(iterable,'__iter__')

# optimized
# only iterators, tuples, lists seem to have __iter__.  String's don't appear to.
# so no need to check for baditer?

def flatten(iterable):
    """Return a flattened iterator."""
    # sanity check: have we been given an iterable?  if not just yield it
    if not hasattr(iterable, "__iter__"):
         yield iterable
         return
    for e in iterable:
         if hasattr(e, "__iter__"):
              # Recurse into iterators.
              for f in flattenNoCheck(e):
                   yield f
         else:
              yield e

def flattenNoCheck(iterable):
    for e in iterable:
         if hasattr(e, "__iter__"):
              # Recurse into iterators.
              for f in flattenNoCheck(e):
                   yield f
         else:
              yield e

def main():
    # test code

    l1 = [1, [2, [3, 4]], 5]

    def foo():
         for x in range(22, 29):
              yield x

    l2 = [1, 2, [3, [4, 5], [6, 7], foo(), [9, 10, 11]]]

    for elem in flatten(l1):
        print elem

    print [x for x in flatten(l2)]


if __name__ == '__main__': main()
