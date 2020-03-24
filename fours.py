from typing import Generator, Tuple

one = {4: ('4', 0), .4: ('.4', 1), 4 / 9: ('.4~', 4),
       24: ('fac(4)', 8), 2: ('sqrt(4)', 8), 6 / 9: ('sqrt(.4~)', 12)}
two = {44: ('44', 0), 4.4: ('4.4', 1), 40 / 9: ('4.4~', 5), .44: ('.44', 1), 3: ('sqrt(4/.4~)', 16)}
three = {444: ('444', 0), 44.4: ('44.4', 1), 4.44: ('4.44', 1), .444: ('.444', 1)}
four = {}


def int_ish(v) -> bool:
    r = round(v, 10)
    return int(r) == r


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


def apply_binary(target: dict, d1: dict, d2: dict, commutative_ops=True) -> None:
    for v1, (e1, s1) in d1.items():
        for v2, (e2, s2) in d2.items():
            for nv, ne, ns in binaries(v1, v2, e1, e2, s1, s2, commutative_ops):
                if int_ish(nv):
                    nv = int(round(nv))
                if -1 < nv < 300 and (nv not in target or target[nv][1] > ns):
                    target[nv] = ne, ns


def fours():
    apply_binary(two, one, one)
    apply_binary(three, two, one)
    apply_binary(three, one, two, commutative_ops=False)
    apply_binary(four, three, one)
    apply_binary(four, two, two)
    apply_binary(four, one, three, commutative_ops=False)


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
