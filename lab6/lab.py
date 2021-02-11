#!/usr/bin/env python3
"""6.009 Lab 6 -- Boolean satisfiability solving"""

import sys

sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


def update_clause(clause, assign):
    """ Updates a clause """

    # get literal whose value has to change

    for literal in clause:
        if literal[0] in assign:
            var = literal[0]
            value = literal[1]

            break

    else:
        return False

    # literal exp evaluates to True

    if (value and assign[var]) or (not value and not assign[var]):
        return True
    # literal exp evaluates to False
    else:
        clause.remove((var, value))

        return False


def update_formula(formula, assign):
    """ Updates a formula """

    f = [c.copy() for c in formula]
    discard = []

    for clause in f:
        res = update_clause(clause, assign)

        if res:
            discard.append(clause)

    for clause in discard:
        f.remove(clause)

    return f


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    raise NotImplementedError


def boolify_scheduling_problem(student_preferences, session_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of session names (strings) that work for that student
    session_capacities: a dictionary mapping each session name to a positive
                        integer for how many students can fit in that session

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up
    We assume no student or session names contain underscores.
    """
    raise NotImplementedError


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
