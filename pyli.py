import math
import collections as co
import operator as op

Symbol = str
List = list
Number = (int, float)


class Procedure(object):
    """A Scheme procedure"""

    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __call__(self, *args):
        env = Env(dict(zip(self.params, args)), self.env)
        return evaluate(self.body, env)


class Env(co.ChainMap):
    """Variant of ChainMap that allows direct updates to inner scopes"""

    def deep_set(self, key, val):
        for mapping in self.maps:
            if key in mapping:
                if isinstance(mapping, Env):
                    mapping.deep_set(key, val)
                else:
                    mapping[key] = val
                return


def tokenize(program):
    """Returns a list of tokens for a given input string"""

    t = program.replace('(', ' ( ').replace(')', ' ) ').split()
    return [integerize(token) for token in t]


def integerize(token):
    """Converts strings corresponding to integers into their equivalents"""

    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def parse(token_list):
    """Converts a list of tokens into something with structure"""

    if len(token_list) == 0:
        raise SyntaxError("Unexpected EOF while reading.")
    t = token_list.pop(0)
    if t == '(':
        L = []
        while token_list[0] != ')':
            L.append(parse(token_list))
        token_list.pop(0)
        return L
    elif t == ')':
        raise SyntaxError('Unexpected "("')
    else:
        return t


def standard_env():
    """Returns a standard environment"""

    env = dict()
    env.update(vars(math))
    env.update({
        '+':          op.add,
        '-':          op.sub,
        '*':          op.mul,
        '/':          op.truediv,
        '//':         op.floordiv,
        '>':          op.gt,
        '<':          op.lt,
        '>=':         op.ge,
        '<=':         op.le,
        '=':          op.eq,
        'abs':        abs,
        'append':     op.add,
        'begin':      (lambda *x:   x[-1]),
        'car':        (lambda x:    x[0]),
        'cdr':        (lambda x:    x[1:]),
        'cons':       (lambda x, y: [x] + y),
        'eq':         op.is_,
        'equal?':     op.eq,
        'length':     len,
        'list':       (lambda *x:   list(x)),
        'list?':      (lambda x:    isinstance(x, List)),
        'map':        map,
        'max':        max,
        'min':        min,
        'not':        op.not_,
        'null?':      (lambda x:    x == []),
        'number?':    (lambda x:    isinstance(x, Number)),
        'procedure?': callable,
        'round':      round,
        'symbol':     (lambda x:    isinstance(x, Symbol))
    })
    return Env(env)


def evaluate(x, env):
    """Evaluates a Scheme program"""

    if isinstance(x, Symbol):
        if x in env:
            return env[x]
        else:
            raise NameError("name {} is not defined".format(x))
    elif not isinstance(x, List):
        return x
    elif x[0] == 'define':
        _, var, expr = x
        env[var] = evaluate(expr, env)
    elif x[0] == 'if':
        _, test, conseq, alt = x
        expr = conseq if evaluate(conseq, env) else alt
        return evaluate(expr, env)
    elif x[0] == 'quote':
        _, exp = x
        return exp
    elif x[0] == 'set!':
        _, var, exp = x
        env.deep_set(var, evaluate(exp, env))
    elif x[0] == 'lambda':
        _, params, body = x
        return Procedure(params, body, env)
    else:
        proc = evaluate(x[0], env)
        args = [evaluate(arg, env) for arg in x[1:]]

        return proc(*args)


def repl():
    """A read-eval-print loop"""
    env = standard_env()
    while True:
        val = evaluate(parse(tokenize(input('pyli >>  '))), env)
        if val is not None:
            print(val)

if __name__ == '__main__':
    repl()
