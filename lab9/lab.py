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

    if tokens.count("(") != tokens.count(")"):
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
                return stack, idx+1
            sub_stack, idx = parse_expression(idx)
            stack.append(sub_stack)

        return stack, idx+1

    return parse_expression(0)[0]


######################
# Built-in Functions #
######################


snek_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
}


##############
# Evaluation #
##############


def evaluate(tree):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    raise NotImplementedError


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()

    pass
