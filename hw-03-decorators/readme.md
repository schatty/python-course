## Decorator Practice

Implement following decorators

* `disable` - disable a decorator by re-assigning the decorator's name to this function
* `decorator` - decorate a decorator so that it inherits the docstrings and stuff
* `countcalls` - decorator that counts calls made to the function decorated
* `memo` - memoize a function so that it caches all return values for faster lookups
* `n_ary` - given binary function f(x, y) return f(x, y, z) = f(x, f(x, z))
* `trace` - trace calls made to function decorated
