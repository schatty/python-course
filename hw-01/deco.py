from functools import update_wrapper, wraps


def disable(f):
	'''
	Disable a decorator by re-assigning the decorator's name
	to this function. For example, to turn off memoization:

	>>> memo = disable

	'''
	def helper(f):
		f = disable
		return f
	return helper
		

def decorator(deco):
	'''
	Decorate a decorator so that it inherits the docstrings
	and stuff from the function it's decorating.

	deco - decorator that we decorate
	'''
	def wrapped(f):
		"""f - function that we decorate with decorated decorator.
		We want that final function that decorated with some decorator (f) 
		has the same properties as the decorator of this function (deco(f))"""
		return update_wrapper(deco(f), f)
	return wrapped


@decorator
def countcalls(f):
	'''Decorator that counts calls made to the function decorated.'''
	def helper(*args):
		helper.calls += 1
		return f(*args)
	helper.calls = 0
	return helper


@decorator
def memo(f):
	'''
	Memoize a function so that it caches all return values for
	faster future lookups.
	'''
	cache = {}
	def helper(*args):
		x = tuple(args)
		if x not in cache:
			cache[x] = f(*args)
		return cache[x]
	return helper


@decorator
def n_ary(f):
	'''
	Given binary function f(x, y), return an n_ary function such
	that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
	'''
	def helper(x, y, z=None):
		if z is None:
			return f(x, y)
		return f(x, f(y, z))
	return helper

@decorator
class trace(object):
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
	def __init__(self, trace):
		self.trace = trace

	def __call__(self, f):
		def tracer(x):
			""" trace all the function calling """
			print(tracer.calls * self.trace, "-->", f.__name__ + "(" + str(x) + ")")
			tracer.calls += 1
			res = f(x)
			tracer.calls -= 1
			print(tracer.calls * self.trace, "<--", f.__name__ + "(" + str(x) + ") == ", res)
			return res

		tracer.calls = 0
		return tracer
		

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
	print("foo attributes: ", foo.__dict__)
	print("foo __wrapper__ was called: ", foo.__wrapped__.calls)
	print("foo was called", foo.calls, "times")

	print(bar(4, 3))
	print(bar(4, 3, 2))
	#print(bar(4, 3, 2, 1))
	print("bar was called", bar.calls, "times")

	print(fib.__name__)
	print(fib.__doc__)
	fib(3)
	print(fib.calls, 'calls made')


if __name__ == '__main__':
    main()
