Four fours
==========

``fours.py`` finds a simple mathematical expression for integers from 0 to 100
using only common mathematical operators and the digit 4.

For example, you can represent 16 as ``4+4+4+4``, 17 as ``4*4+4/4``, and
18 as ``44*.4-.4``.
The `Wikipedia page <https://en.wikipedia.org/wiki/Four_fours>`_ gives more
information and some history.

There are various rules about what operations are allowed. For this example,
the allowed operators are:


+--------------------+-------------------------+----------------+
| Operator           | Example                 | Value          |
+====================+=========================+================+
| addition           | ``4+4``                 | 8              |
+--------------------+-------------------------+----------------+
| subtraction        | ``4-4``                 | 0              |
+--------------------+-------------------------+----------------+
| multiplication     | ``4*4``                 | 16             |
+--------------------+-------------------------+----------------+
| division           | ``4/4``                 | 1              |
+--------------------+-------------------------+----------------+
| exponentiation     | ``pow(4,4)``            | 256            |
+--------------------+-------------------------+----------------+
| square root        | ``sqrt(4)``             | 2              |
+--------------------+-------------------------+----------------+
| factorial (4!)     | ``fac(4)``              | 24             |
+--------------------+-------------------------+----------------+
| decimal point      | ``.4`` or ``4.4``       | .4 or 4.4      |
+--------------------+-------------------------+----------------+
| overline           | ``.4~``                 | .4444444444444 |
+--------------------+-------------------------+----------------+


The general approach I take here is to start with expressions involving
a single 4, and then successively combine these shorter expressions to make
longer expressions.

There are four python dictionaries, each one representing expressions with a
certain number of 4s. The key in each key-value pair in the dictionary is the
value of an expression, and the value is a 2-tuple of a string (representing
the expression to generate the value) and an integer representing the `niceness`
score of the expression. The niceness score
is a subjective opinion of how 'nice' an expression is - I'm looking for the nicest
(lowest score) expression for each of the numbers form 0-100.


First, I need to prime the dictionaries holding the expressions:

.. code:: python

    one = {4: ('4', 0), .4: ('.4', 1), 4 / 9: ('.4~', 4),
           24: ('fac(4)', 8), 2: ('sqrt(4)', 8), 6 / 9: ('sqrt(.4~)', 12)}
    two = {44: ('44', 0), 4.4: ('4.4', 1), 40 / 9: ('4.4~', 5), .44: ('.44', 1), 3: ('sqrt(4/.4~)', 16)}
    three = {444: ('444', 0), 44.4: ('44.4', 1), 4.44: ('4.44', 1), .444: ('.444', 1)}
    four = {}

You might notice that I haven't been exhaustive in listing all possible values
and expressions. There's no ``sqrt(sqrt(4))`` in the ``one`` dictionary, for example.
And some rational values are omitted as their equations aren't very 'nice', such as
8/125 using 2 fours: ``sqrt(sqrt(sqrt(.4^4!)))`` and 1/8 using 2 fours:
``sqrt(sqrt(sqrt(sqrt(4**-4!))))``


I also need a helper function to determine whether a number is an integer:

.. code:: python

    def int_ish(v):
        r = round(v, 10)
        return int(r) == r

The ``int_ish`` function determines if a number is close enough to an integer to be
considered an integer. Due to the
inaccuracies of floating point arithmetic, sometimes a number that
should be an integer is
instead *almost* an integer. For example:

.. code:: python

    >>> from math import sqrt
    >>> sqrt(2) * sqrt(2)  # should be 2
    2.0000000000000004
    >>> sqrt(3) * sqrt(3)
    2.9999999999999996


So I use ``int_ish`` to tell if I can safely ``round()`` a number to an int.
Most of the time this is good enough, but I came across one case, 444 to the power
of -4 (``444**-4``), which is so close to zero that int_ish thinks it is zero.

There's a generator function for yielding results for the 5 binary operators:

.. code:: python

    def binaries(v1, v2, e1: str, e2: str, s1: int, s2: int, commutative_ops=True) \
            -> Generator[Tuple[float, str, int], None, None]:
        if commutative_ops:
            yield v1 + v2, f'({e1}+{e2})', s1 + s2 + 1
            yield v1 * v2, f'({e1}*{e2})', s1 + s2 + 3
        yield v1 - v2, f'({e1}-{e2})', s1 + s2 + 2
        if v2 != 0:
            yield v1 / v2, f'({e1}/{e2})', s1 + s2 + 4
        if v1 > 0 and abs(v2) <= 8:
            yield v1 ** v2, f'pow({e1}, {e2})', s1 + s2 + 8

The standard four operators are straightforward, with only division needing
to be protected from divide by zero. Exponentiation ('power of') is
a little bit tricky. I use some crude pruning to exclude values which
are likely to lead to very large (or very tiny) numbers that would
be unlikely to lead to expressions in our target range of 0-100.

Also, since addition and multiplication are commutative (``a + b = b + a``), there
are some cases where I can tell that I don't need to do ``b + a`` because
we've already done ``a + b``. The ``commutative_ops`` parameter is there to control
this optimisation.

It turns out that exponentiation is not actually needed
to get an expression for all the
numbers from 0-100, but with a niceness penalty of 8, it results
in some 'nicer' expressions than without.

Here's a table with a few examples. Notice that for the value 81, both
expressions have a score of 14, but the expression involving power was
found first, and only the first expression found for a certain score is
remembered.

===== ======================== ===== = =========================== ======
value with exponentiation      score    without exponentiation     score
----- ------------------------ ----- - --------------------------- ------
   63 (pow(4, 4)-4)/4           *14*    ((fac(4)-.4)/.4)+4          *17*
   77 pow((4/.4~), sqrt(4))-4   *26*    ((fac(4)-.4~)/.4~)+fac(4)   *31*
   81 pow((4-(4/4)), 4)         *14*    (4-.4)/(.4~-.4)             *14*
===== ======================== ===== = =========================== ======

Are the expressions on the right less nice than the expressions on the left?
Maybe. It's an imperfect measure, but it's the only measure I have.

I need a function for taking two dictionaries, applying the operators to the
contents of each, and populating a third dictionary with the results:

.. code:: python

    def apply_binary(target: dict, d1: dict, d2: dict, commutative_ops=True) -> None:
        for v1, (e1, s1) in d1.items():
            for v2, (e2, s2) in d2.items():
                for nv, ne, ns in binaries(v1, v2, e1, e2, s1, s2, commutative_ops):
                    if int_ish(nv):
                        nv = int(round(nv))
                    if -1 < nv < 300 and (nv not in target or target[nv][1] > ns):
                        target[nv] = ne, ns

The ``apply_binary`` function populates a target dictionary by combining
values from the two source dictionaries with one of the binary operators.
The first two ``for`` loops ensure I have every combination of values from
the two dictionaries. The innermost third ``for`` loop ensures I try every
binary operator. The ``nv, ne, ns`` variables are short for "new value",
"new expression", and "new score". First I convert ``nv`` to an int if it looks
like it should be one, then add the new value to the target dictionary if
it's within a 'reasonable' range and it's not been seen before or the new score
is better (lower) than an expression that's been seen before.

The final function ties it all together:

.. code:: python

    def fours():
        apply_binary(two, one, one)
        apply_binary(three, two, one)
        apply_binary(three, one, two, commutative_ops=False)
        apply_binary(four, three, one)
        apply_binary(four, two, two)
        apply_binary(four, one, three, commutative_ops=False)

Four each of the four dictionaries, I have all the possible combinations
of pairs that can add up to that number, and apply the binary operations to
them. I'm 'counting' the number of fours in an expression, so for 3 fours
I can do both
"<1-four-expression> <binary-op> <2-fours-expression>" as well as the
other way around. And for 4 fours there are 3 combinations (1+3, 2+2, and 3+1).
The ``commutative_ops`` parameter determines whether I should do commutative
operations - it's just a minor optimisation to prevent unnecessary additions
and multiplications.

The main entrypoint times the calculation and performs a double check using python's own expression parser:

.. code:: python

    if __name__ == '__main__':
        import time
        from math import sqrt, factorial as fac

        start = time.time()
        fours()
        end = time.time()

        s4 = {v: e for v, e in four.items() if int_ish(v) and 100 >= v >= 0}
        for num, (equation, score) in sorted(s4.items()):
            val = round(eval(equation.replace('.4~', '(4/9)')), 10)
            print(f'{num:3}', equation, f'(score {score})', '!!!!!!!!!' if num != val else '')
        print(f'seconds: {end - start}')
        niceness = sum(x[1] for x in s4.values())
        print(f'length: {len(s4)}, total niceness {niceness} (avg: {round(niceness / len(s4), 3)})')

The ``s4`` dictionary uses s dictionary comprehension to get the expressions that were found
that are in the range I care about (0 to 100). A string replace of ``.4~`` with (4/9) along with
the importing ``sqrt`` and the factorial function as ``fac`` ensure that the expression is legal python.
The expression is printed out, with a warning of exclamation marks if the evaluation of the expression
in python is not what I expected.

The final output:

.. code:: text

      0 (44-44) (score 2)
      1 (44/44) (score 4)
      2 (4-((4+4)/4)) (score 7)
      3 (((4+4)+4)/4) (score 6)
      4 (((4-4)*4)+4) (score 6)
      5 (((4*4)+4)/4) (score 8)
      6 (((4+4)/4)+4) (score 6)
      7 ((44/4)-4) (score 6)
      8 (((4+4)-4)+4) (score 4)
      9 (((4/4)+4)+4) (score 6)
     10 (44/4.4) (score 5)
     11 ((4/4)+(4/.4)) (score 10)
     12 ((44+4)/4) (score 5)
     13 (((4-.4)/.4)+4) (score 9)
     14 (((4-.4)*4)-.4) (score 9)
     15 ((44/4)+4) (score 5)
     16 (((4+4)+4)+4) (score 3)
     17 ((4*4)+(4/4)) (score 8)
     18 ((44*.4)+.4) (score 6)
     19 (((4+4)-.4)/.4) (score 9)
     20 (((4/4)+4)*4) (score 8)
     21 ((4.4+4)/.4) (score 7)
     22 (((4+4)/.4~)+4) (score 10)
     23 (((4*fac(4))-4)/4) (score 17)
     24 (((4*4)+4)+4) (score 5)
     25 ((4*4)+(4/.4~)) (score 12)
     26 ((4*4)+(4/.4)) (score 9)
     27 (((4+4)+4)/.4~) (score 10)
     28 (44-(4*4)) (score 5)
     29 ((4/(.4*.4))+4) (score 10)
     30 (((4+4)+4)/.4) (score 7)
     31 (((4+fac(4))/4)+fac(4)) (score 22)
     32 ((4*4)+(4*4)) (score 7)
     33 (((4-.4)/.4)+fac(4)) (score 17)
     34 (44-(4/.4)) (score 7)
     35 (44-(4/.4~)) (score 10)
     36 (44-(4+4)) (score 3)
     37 (((4*4)+.4~)/.4~) (score 16)
     38 (44-(4+sqrt(4))) (score 11)
     39 (((4*4)-.4)/.4) (score 11)
     40 (((4*4)/.4~)+4) (score 12)
     41 (((4*4)+.4)/.4) (score 10)
     42 ((44-4)+sqrt(4)) (score 11)
     43 (44-(4/4)) (score 6)
     44 ((44+4)-4) (score 3)
     45 (44+(4/4)) (score 5)
     46 ((44+4)-sqrt(4)) (score 11)
     47 (44+sqrt(4/.4~)) (score 17)
     48 (((4+4)+4)*4) (score 5)
     49 (44+(sqrt(4)/.4)) (score 14)
     50 (((4*4)+4)/.4) (score 9)
     51 (((.4+fac(4))-4)/.4) (score 17)
     52 ((44+4)+4) (score 2)
     53 (44+(4/.4~)) (score 9)
     54 (44+(4/.4)) (score 6)
     55 (44/(.4+.4)) (score 7)
     56 (((4/.4)+4)*4) (score 9)
     57 (((.4+fac(4))/.4)-4) (score 17)
     58 ((fac(4)-(.4+.4))/.4) (score 18)
     59 (((4+fac(4))/.4~)-4) (score 19)
     60 (44+(4*4)) (score 4)
     61 ((4/4)+(fac(4)/.4)) (score 18)
     62 (((4*4)*4)-sqrt(4)) (score 16)
     63 ((pow(4, 4)-4)/4) (score 14)
     64 ((4+4)*(4+4)) (score 5)
     65 ((pow(4, 4)+4)/4) (score 13)
     66 (((4*4)*4)+sqrt(4)) (score 15)
     67 (((4+fac(4))/.4~)+4) (score 18)
     68 (((4*4)*4)+4) (score 7)
     69 (((4-.4)+fac(4))/.4) (score 17)
     70 ((44/sqrt(.4~))+4) (score 17)
     71 ((4.4+fac(4))/.4) (score 15)
     72 ((44+4)+fac(4)) (score 10)
     73 (((fac(4)+fac(4))+sqrt(.4~))/sqrt(.4~)) (score 46)
     74 (((4+fac(4))/.4)+4) (score 15)
     75 ((44/.4~)-fac(4)) (score 18)
     76 (((fac(4)-4)*4)-4) (score 15)
     77 (pow(sqrt(4/.4~), 4)-4) (score 26)
     78 (((fac(4)-4)*4)-sqrt(4)) (score 23)
     79 (((.4~+fac(4))/.4~)+fac(4)) (score 30)
     80 (((4*4)+4)*4) (score 7)
     81 pow((4-(4/4)), 4) (score 14)
     82 (((fac(4)-4)*4)+sqrt(4)) (score 22)
     83 (((fac(4)-.4)/.4)+fac(4)) (score 25)
     84 ((44*sqrt(4))-4) (score 13)
     85 (((4/.4)+fac(4))/.4) (score 19)
     86 ((4/(.4~-.4))-4) (score 13)
     87 ((4*fac(4))-(4/.4~)) (score 21)
     88 (44+44) (score 1)
     89 (((fac(4)+sqrt(4))/.4)+fac(4)) (score 31)
     90 ((44-4)/.4~) (score 10)
     91 ((4*fac(4))-(sqrt(4)/.4)) (score 26)
     92 ((44*sqrt(4))+4) (score 12)
     93 ((4*fac(4))-sqrt(4/.4~)) (score 29)
     94 ((4/(.4~-.4))+4) (score 12)
     95 ((44/.4~)-4) (score 10)
     96 ((44+4)*sqrt(4)) (score 12)
     97 ((4/4)+(4*fac(4))) (score 16)
     98 ((44-.4~)/.4~) (score 14)
     99 (4.4/(.4~-.4)) (score 12)
    100 (44/.44) (score 5)
    seconds: 0.33713221549987793
    length: 101, total niceness 1201 (avg: 11.891)

Extensions
----------

In approximate order of difficulty:

* Change the niceness scores to match your tastes.
* Add other unary or binary operators. Or remove some. What's the minimum set of
  operators that will yield an expression for each value 0-100?
* In the function ``fours()``, Ar all the function
  calls to ``apply_binary`` necessary to find the nicest expressions?
  Or what combination results in the fastest complete result (even if it's not the nicest)?
* If a value has multiple expressions with the minimum niceness score,
  display those expressions also.
* As well as displaying the niceness score, also display the number of expressions
  found for each number.
* Despite the ``commutative_ops`` parameter, some commutative operations are
  still done twice: when ``apply_binary`` is called
  with two source dictionaries of the same size. For example: 4+.4 and .4+4 will
  both be calculated when ``apply_binary(two, one, one)`` is called. Is it worth
  trying to eliminate this extra work, considering run time and code complexity?
* Instead of generating normal infix notation for expressions,
  generate postfix (`reverse polish
  <https://en.wikipedia.org/wiki/Reverse_Polish_notation>`_) notation. Postfix
  has the advantage of not needing parentheses to unambiguously describe an expression.
* Remove unnecessary parentheses.

  - Approach 1: Add operator precedence information
    for each expression, and use that information to determine whether to use
    parentheses.
  - Approach 2: Generate postfix expressions initially, and then use
    a postfix-to-infix algorithm. This is probably faster and nicer,
    and more flexible (you could generate other representations, e.g. LaTeX, from
    the same intermediate postfix representation)
* Instead of four 4s, use the digits 1,2,3,4 (or some other sequence of digits)
  ensuring that the digits remain in the same order when reading the expression.
  So 1+2+3+4 is allowed (in order), but 4+3+2+1 is not (out of order).


