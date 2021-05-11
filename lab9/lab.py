#!/usr/bin/env python3
"""6.009 Lab 9: Snek Interpreter"""

import doctest

# NO ADDITIONAL IMPORTS!


###########################
# Snek-related Exceptions #
###########################

class SnekError(Exception):
    """
    A type of exception to be raised if there is an error with a Snek
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """
    pass


class SnekSyntaxError(SnekError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    pass


class SnekNameError(SnekError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    pass


class SnekEvaluationError(SnekError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SnekNameError.
    """
    pass


############################
# Tokenization and Parsing #
############################


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Snek
                      expression
    """
    lines = source.split("\n")

    line_tokens = []

    # handle each line one by one

    for line in lines:
        tokens = []
        word = ''
        # check each character

        for c in line:

            if c == "(":
                tokens.append(c)

            # if its closing parenthesis,
            # does it has a symbol or number just before it?
            elif c == ")":
                if word != '':
                    tokens.append(word)
                    word = ''
                tokens.append(c)

            elif c.isspace() and word != '':
                tokens.append(word)
                word = ''

            # if comment starts, append previous tokens (if any) and break
            elif c == ";":
                break
            else:
                if c != " ":
                    word += c

        if word != "" and word != " ":
            tokens.append(word)

        if len(tokens) != 0:
            line_tokens.append(tokens)

    return [t for tokens in line_tokens for t in tokens]  # merge list of lists


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """

    def is_balanced(lst):
        # check for balanced parenthesis
        queue = []

        for e in lst:
            if e == "(":
                queue.append(e)
            elif e == ")":
                if not queue:
                    return False
                queue.remove("(")

        return not queue

    if not is_balanced(tokens):
        raise SnekSyntaxError

    if len(tokens) > 1 and "(" not in tokens:
        raise SnekSyntaxError

    def change_dtype(string):
        # try int, then float, then return as it is
        try:
            return int(string)
        except ValueError:
            try:
                return float(string)
            except ValueError:
                return string

    def is_valid_stack(stack):
        if stack[0] == ":=" and len(stack) != 3:
            return False

        if stack[0] == ":=" and isinstance(change_dtype(stack[1]), (int, float)) and isinstance(change_dtype(stack[2]), (int, float)):
            return False

        return True

    def parse_expression(idx):
        # return numbers and symbols as it is

        if tokens[idx] != "(":
            return change_dtype(tokens[idx]), idx+1

        # for S-expression
        # keep adding numbers, symbols and sub_stacks to stack until ")"
        idx += 1
        stack = []

        while idx < len(tokens):
            if tokens[idx] == ")":
                if not is_valid_stack(stack):
                    raise SnekSyntaxError

                return stack, idx+1
            sub_stack, idx = parse_expression(idx)
            stack.append(sub_stack)

        if not is_valid_stack(stack):
            raise SnekSyntaxError

        return stack, idx+1

    return parse_expression(0)[0]


######################
# Built-in Functions #
######################


def prod(args):
    if len(args) == 0:
        return 1

    result = 1

    for num in args:
        result *= num

    return result


def div(args):
    if len(args) == 0:
        raise SnekError

    if len(args) == 1:
        return 1/args[0]

    result = args[0]

    for num in args[1:]:
        result /= num

    return result


snek_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': prod,
    '/': div}


##############
# Evaluation #
##############

class Environment(object):
    def __init__(self, parent=None, bindings={}):
        self.parent = parent
        self.bindings = bindings


builtin_env = Environment(bindings=snek_builtins)

def get_value(symbol, env):
    """
    >>> env = Environment(parent=Environment(None, snek_builtins))
    >>> symbol = "+"
    >>> get_value(symbol, env) == sum
    True
    """

    while True:
        if symbol in env.bindings:
            return env.bindings[symbol]

        if env.parent is None:
            break
        env = env.parent


def evaluate(tree, env=None):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function

    """

    if env is None:
        env = Environment(builtin_env)

    if isinstance(tree, (int, float)):
        return tree

    if not isinstance(tree, list):
        symbol_val = get_value(tree, env)

        if symbol_val is None:
            raise SnekNameError

        return symbol_val

    if tree[0] == ":=":
        expr_val = evaluate(tree[2], env)
        env.bindings[tree[1]] = expr_val

        return expr_val

    if tree[0] not in snek_builtins:
        raise SnekEvaluationError

    symbol_val = evaluate(tree[0], env)

    if len(tree) < 2:
        return symbol_val
    args = [evaluate(t) for t in tree[1:]]

    result = symbol_val(args)

    return result



def result_and_env(tree, env=None):
    if env is None:
        env = Environment(builtin_env)
    result = evaluate(tree, env)

    return (result, env)


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()

    # REPL
    inp = ""

    while inp.lower() != "quit":
        try:
            inp = input("in> ")
            tokens = tokenize(inp)
            parsed = parse(tokens)
            result = evaluate(parsed)
            print(result)
        except:
            continue
