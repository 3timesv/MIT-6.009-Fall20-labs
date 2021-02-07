#!/usr/bin/env python3
import os
import lab
import sys
import pickle
import doctest

import pytest

sys.setrecursionlimit(20000)

TEST_DIRECTORY = os.path.dirname(__file__)

TESTDOC_FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
TESTDOC_SKIP = ['lab']


def test_doctests_run():
    """ Checking to see if all lab doctests run successfully """
    results = doctest.testmod(lab, optionflags=TESTDOC_FLAGS, report=False)
    assert results[0] == 0


def test_all_doc_strings_exist():
    """ Checking if docstrings have been written for everything in lab.py """
    tests = doctest.DocTestFinder(exclude_empty=False).find(lab)
    for test in tests:
        if test.name in TESTDOC_SKIP:
            continue
        assert test.docstring, f"Oh no, '{test.name}' has no docstring!"


def test_newsmallgame():
    result = lab.new_game_2d(10, 8, [(7, 3), (2, 6), (8, 7), (4, 4), (3, 5),
                                     (4, 6), (6, 2), (9, 4), (4, 2), (4, 0),
                                     (8, 6), (9, 7), (8, 5), (5, 0), (7, 2),
                                     (5, 3)])
    expected = {"board": [[0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 1, 1, 1],
                          [0, 0, 0, 0, 1, 2, ".", 1],
                          [1, 2, 1, 2, 2, ".", 3, 2],
                          [".", 3, ".", 3, ".", 3, ".", 1],
                          [".", 4, 3, ".", 2, 2, 1, 1],
                          [1, 3, ".", 4, 2, 0, 0, 0],
                          [0, 2, ".", ".", 2, 2, 3, 2],
                          [0, 1, 2, 3, 3, ".", ".", "."],
                          [0, 0, 0, 1, ".", 3, 4, "."]],
                "dimensions": (10, 8),
                "mask": [[False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False]],
                "state": "ongoing"}
    for name in expected:
        assert result[name] == expected[name]


def test_newmediumgame():
    result = lab.new_game_2d(30, 16, [(16, 6), (17, 7), (14, 4), (13, 4),
                                      (0, 7), (21, 6), (2, 5), (5, 5), (6, 10),
                                      (12, 6), (24, 14), (14, 1), (24, 1),
                                      (26, 12), (8, 15), (9, 3), (16, 0),
                                      (19, 13), (15, 14), (13, 10), (18, 10),
                                      (21, 15), (28, 15), (29, 14), (11, 15),
                                      (14, 8), (17, 8), (24, 8), (25, 5),
                                      (2, 1), (10, 3), (27, 2), (17, 6),
                                      (7, 15), (15, 0), (21, 8), (20, 0),
                                      (1, 10), (10, 4), (14, 6), (1, 0),
                                      (4, 11), (27, 0), (9, 13), (23, 5),
                                      (14, 12), (20, 15), (3, 15), (26, 14),
                                      (4, 8), (10, 15), (7, 11), (18, 1),
                                      (25, 4), (26, 3), (22, 14), (28, 2),
                                      (13, 2), (19, 6), (1, 4), (21, 4),
                                      (1, 9), (8, 7), (23, 1), (22, 11),
                                      (19, 5), (18, 7), (0, 6), (26, 4),
                                      (3, 4), (5, 9), (24, 13), (20, 8),
                                      (19, 0), (0, 3), (21, 13), (3, 3),
                                      (28, 9), (11, 1), (12, 10), (24, 10),
                                      (18, 13), (0, 0), (21, 0), (3, 13),
                                      (27, 13), (5, 15), (26, 9), (17, 4),
                                      (7, 9), (19, 9), (24, 7), (22, 5),
                                      (3, 8), (27, 8), (9, 5), (23, 13),
                                      (5, 2), (10, 2)])
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', 'test2d_newmediumgame.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    for name in expected:
        assert result[name] == expected[name]


def test_newlargegame():
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', 'test2d_newlargegame.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', 'test2d_newlargegame.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    result = lab.new_game_2d(inputs['num_rows'], inputs['num_cols'],
                         inputs['bombs'])
    for name in expected:
        assert result[name] == expected[name]


@pytest.mark.parametrize('test', ['complete', 'mine', 'small'])
def test_dig_2d(test):
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', f'test2d_dig{test}.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', f'test2d_dig{test}.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    game = inputs['game']
    revealed = lab.dig_2d(game, inputs['row'], inputs['col'])
    assert revealed == expected['revealed']
    for name in expected['game']:
        assert game[name] == expected['game'][name]


def test_render_2d():
    """ Testing render on a small board """
    with open(os.path.join(TEST_DIRECTORY, 'test_inputs', 'test2d_render.pickle'), 'rb') as f:
        inp = pickle.load(f)
    result = lab.render_2d(inp)
    expected = [[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' ', '1', '1', '1'],
                [' ', ' ', ' ', ' ', '1', '2', '_', '_'],
                ['1', '2', '1', '2', '2', '_', '_', '_'],
                ['_', '_', '_', '_', '_', '_', '_', '_'],
                ['_', '_', '_', '_', '_', '_', '_', '_'],
                ['_', '_', '_', '_', '_', '_', '_', '_'],
                ['_', '_', '_', '_', '_', '_', '_', '_'],
                ['_', '_', '_', '_', '_', '_', '_', '_'],
                ['_', '_', '_', '_', '_', '_', '_', '_']]
    assert result == expected

def test_asciismall():
    """ Testing render_ascii on a small 2d board """
    with open(os.path.join(TEST_DIRECTORY, 'test_inputs', 'test2d_asciismall.pickle'), 'rb') as f:
        inp = pickle.load(f)
    result = lab.render_ascii(inp)
    expected = ('        \n'
                '     111\n'
                '    12__\n'
                '12122___\n'
                '________\n'
                '________\n'
                '________\n'
                '________\n'
                '________\n'
                '________')
    assert result == expected

def test_asciixray():
    """ Testing render_ascii on a small 2d board with xray """
    with open(os.path.join(TEST_DIRECTORY, 'test_inputs', 'test2d_asciixray.pickle'), 'rb') as f:
        inputs = pickle.load(f)
    result = lab.render_ascii(inputs['game'], True)
    expected = ('        \n'
                '     111\n'
                '    12.1\n'
                '12122.32\n'
                '.3.3.3.1\n'
                '.43.2211\n'
                '13.42   \n'
                ' 2..2232\n'
                ' 1233...\n'
                '   1.34.')
    assert result == expected


@pytest.mark.parametrize('test', [1, 2, 3])
def test_2d_integration(test):
    """ dig, render, and render_ascii on boards """
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', f'test2d_integration{test}.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', f'test2d_integration{test}.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    results = []
    game = inputs['game']
    for location, exp in zip(inputs['coords'], expected):
        result = (('dig', lab.dig_2d(game, *location)),
                  ('game', game),
                  ('render', lab.render_2d(game)),
                  ('render/xray', lab.render_2d(game, True)),
                  ('render_ascii', lab.render_ascii(game)),
                  ('render_ascii/xray', lab.render_ascii(game, True)))
        assert result == exp


def test_newsmall6dgame():
    """ Testing new_game on a small 6-D board """
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', 'testnd_newsmall6dgame.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', 'testnd_newsmall6dgame.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    result = lab.new_game_nd(inputs['dimensions'], inputs['bombs'])
    for i in ('dimensions', 'board', 'mask', 'state'):
        assert result[i] == expected[i]


def test_newlarge4dgame():
    """ Testing new_game on a large 4-D board """
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', 'testnd_newlarge4dgame.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', 'testnd_newlarge4dgame.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    result = lab.new_game_nd(inputs['dimensions'], inputs['bombs'])
    for i in ('dimensions', 'board', 'mask', 'state'):
        assert result[i] == expected[i]


@pytest.mark.parametrize('test', [1,2,3])
def test_nd_integration(test):
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', f'testnd_integration{test}.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', f'testnd_integration{test}.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    g = lab.new_game_nd(inputs['dimensions'], inputs['bombs'])
    for location, results in zip(inputs['digs'], expected):
        squares_revealed, game, rendered, rendered_xray = results
        res = lab.dig_nd(g, location)
        assert res == squares_revealed
        for i in ('dimensions', 'board', 'mask', 'state'):
            assert g[i] == game[i]
        assert lab.render_nd(g) == rendered
        assert lab.render_nd(g, True) == rendered_xray


if __name__ == '__main__':
    import sys
    import json

    class TestData:
        def __init__(self):
            self.results = {'passed': []}

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtestloop(self, session):
            yield

        def pytest_runtest_logreport(self, report):
            if report.when != 'call':
                return
            self.results.setdefault(report.outcome, []).append(report.head_line)

        def pytest_collection_finish(self, session):
            self.results['total'] = [i.name for i in session.items]

        def pytest_unconfigure(self, config):
            print(json.dumps(self.results))

    if os.environ.get('CATSOOP'):
        args = ['--color=yes', '-v', __file__]
        if len(sys.argv) > 1:
            args = ['-k', sys.argv[1], *args]
        kwargs = {'plugins': [TestData()]}
    else:
        args = ['-v', __file__] if len(sys.argv) == 1 else ['-v', *('%s::%s' % (__file__, i) for i in sys.argv[1:])]
        kwargs = {}
    res = pytest.main(args, **kwargs)
