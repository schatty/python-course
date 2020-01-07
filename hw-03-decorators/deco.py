from functools import wraps


def disable():
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    '''
    return


def decorator():
    '''
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    '''
    return


def countcalls(func):
    '''Decorator that counts calls made to the function decorated.'''
    def wrapper(*args, **kwargs):
        wrapper.calls['n'] += 1
        res = func(*args, **kwargs)
        return res

    wrapper.calls = {'n': 0}
    return wrapper


def memo(func):
    ''' Memoize a function so that it caches all
    return values for faster future lookups.  '''
    cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        lookup = tuple(list(args) +
                       [f"{k}{kwargs[k]}" for k in sorted(kwargs)])
        if tuple(args) in cache:
            print(f"Returning memoized value for {args}, {kwargs}")
            return cache[lookup]
        res = func(*args, **kwargs)
        cache[lookup] = res
        return res

    return wrapper


def n_ary(func):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''
    def wrapper(*args, **kwargs):
        if len(args) == 1:
            return args[0]
        elif len(args) == 2:
            return func(*args, **kwargs)
        else:
            res = func(args[0], wrapper(*args[1:]))
            return res
    return wrapper


def trace(fill):
    '''Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            pad = decorator.padding
            print(f"{pad}--> {func.__name__}({args[0]})")
            decorator.padding += fill
            res = func(*args, **kwargs)
            decorator.padding = decorator.padding[:-len(fill)]
            print(f"{pad}<-- {func.__name__}({args[0]}) == {res}")
            return res
        return wrapper

    decorator.padding = ""
    return decorator


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, 'calls made')


if __name__ == '__main__':
    main()
