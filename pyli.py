import math
import operator as op

Symbol = str
List = list
Number = (int, float)


def tokenize(program):
    """returns a list of tokens for a given input string"""
    t = program.replace('(', ' ( ').replace(')', ' ) ').split()
    return [integerize(token) for token in t]


def integerize(token):
    """converts strings corresponding to integers into their equivalents"""
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def parse(token_list):
    """converts a list of tokens into something with structure"""
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
    """returns a standard environment"""
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
    return env


def evaluate(x, env):
    """evaluates program"""
    if isinstance(x, Symbol):
        return env[x]
    elif not isinstance(x, List):
        return x
    elif x[0] == 'define':
        (_, var, expr) = x
        env[var] = evaluate(expr, env)
    elif x[0] == 'if':
        (_, test, conseq, alt) = x
        expr = (conseq if evaluate(conseq, env) else alt)
        return evaluate(expr, env)
    else:
        proc = evaluate(x[0], env)
        args = [evaluate(arg, env) for arg in x[1:]]

        return proc(*args)


def repl():
    """a read-eval-print loop"""
    while True:
        val = evaluate(parse(tokenize(input('pyli >>  '))), standard_env())
        if val is not None:
            print(val)
