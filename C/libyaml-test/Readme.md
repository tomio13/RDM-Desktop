# libyaml test
a simple test how to use the yaml library in C.

# compile
use:
```bash
gcc libyaml-blocks.c -o yaml-test -lyaml
```

# test to find key-value pairs
After working a bit on the yaml structure, I found that:
* if mapping is ON, we have pairs of scalar calls first key, then value
* if mapping is off, we have only values
* when a new mapping comes into mapping or a new sequence shows up,
  the last scalar value turns to be a key

Implemented a recursive algorithm to handle this. It is not nice, but
seems to work fine.
Source: libyaml-test-events-new.c
Compile it with:
```bash
gcc -Wall libyaml-test-events-new.c -o yaml-test -lyaml
```
