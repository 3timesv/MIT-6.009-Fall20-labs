#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """

    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')

            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


def copy(array):
    """
    Copies multidimensional array recursively.

    Args:
        array (list): list of lists/ objects

    Returns:
        (list): copy of array
    """

    if not isinstance(array[0], list):
        return [e for e in array]

    return [copy(subarray) for subarray in array]


def init_array(dimensions, value):
    """
    Initialize a n dimensional array.

    Args:
        dimensions (tuple): Dimensions of the array
        value : initialization value

    Returns:
        resulting array
    """

    depth = len(dimensions)

    def build(d):
        if d == 1:
            return [value] * dimensions[-1]

        return [build(d-1) for _ in range(dimensions[-d])]

    return build(depth)


def get_value(array, coordinates):
    """
    Returns the value at coordinates in the array.

    Args:
        array (list): N-d array as list of lists
        coordinates (tuple/ list): coordinates

    Returns:
        (tuple/ list): value at coordinates
    """
    result = array.copy()

    for c in coordinates:
        result = result[c]

    return result


def assign_value(array, coordinates, value):
    """
    Assigns value at coordinates in array.

    Args:
        array (list): N-d array as list of lists
        coordinates (tuple/ list): coordinates
        value : value to assign

    Returns:
        list with assigned value at coordinates
    """

    def assign(arr, idx):
        if idx == len(coordinates) - 1:
            arr[coordinates[idx]] = value
        else:
            assign(arr[coordinates[idx]], idx+1)

    assign(array, 0)


def get_coordinates_gen(dimensions):
    """
    Get coordinates generator of N-dimensional array.

    Args:
        dimensions (tuple/ list): dimensions of array

    Returns:
        coordinates generator
    """
    def inner(dim):

        if dim == len(dimensions) - 1:
            for i in range(dimensions[dim]):
                yield i
        elif dim == len(dimensions) - 2:
            for i in range(dimensions[dim]):
                for p in inner(dim + 1):
                    yield tuple([i] + [p])
        else:
            for i in range(dimensions[dim]):
                for p in inner(dim + 1):
                    yield tuple([i] + list(p))

    return inner(0)


def get_neighbors_relative_coordinates(dimensions):
    """
    Get neighbors' relative coordinates.
    """

    one_d = [-1, 0, 1]

    def inner(dim):
        if dim == len(dimensions) - 1:
            return [i for i in one_d]

        prev = inner(dim+1)
        nxt = []

        if dim == len(dimensions) - 2:
            for i in one_d:
                nxt.extend([i]+[e] for e in prev)
        else:
            for i in one_d:
                nxt.extend([i]+e for e in prev)

        return nxt

    return inner(0)


def get_neighbors_coordinates(coord, rel, dimensions):
    """
    Get neighbors' coordinates.

    Args:
        coord (tuple/ list): coordinates whose neighbor is required
        rel (list of tuples): neighbors' relative coordinates
        dimensions (tuple): dimensions of board

    Returns:
        list of tuples: neighbors' coordinates
    """
    neighbor_coords = []

    for r in rel:
        n_c = [c+o for c, o in zip(coord, r)]
        valids = [(0 <= c < dimensions[i]) for i, c in enumerate(n_c)]

        if False in valids:
            continue
        else:
            neighbor_coords.append(tuple(n_c))

    return neighbor_coords

# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    board = []
    mask = []

    for r in range(num_rows):
        row = []
        mask_row = []

        for c in range(num_cols):
            mask_row.append(False)

            if [r, c] in bombs or (r, c) in bombs:
                row.append('.')
            else:
                row.append(0)

        mask.append(mask_row)
        board.append(row)

    for r in range(num_rows):
        for c in range(num_cols):
            if board[r][c] == 0:
                neighbor_bombs = 0

                for x in [-1, 0, 1]:
                    for y in [-1, 0, 1]:
                        if (0 <= r+x < num_rows) and (0 <= c+y < num_cols):
                            if board[r+x][c+y] == '.':
                                neighbor_bombs += 1

                board[r][c] = neighbor_bombs

    return {
        'dimensions': (num_rows, num_cols),
        'board': board,
        'mask': mask,
        'state': 'ongoing'}


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat
    """

    if game['state'] == 'defeat' or game['state'] == 'victory':
        return 0

    if game['board'][row][col] == '.':
        game['mask'][row][col] = True
        game['state'] = 'defeat'

        return 1

    bombs = 0
    covered_squares = 0

    for r in range(game['dimensions'][0]):
        for c in range(game['dimensions'][1]):
            if game['board'][r][c] == '.':
                if game['mask'][r][c] == True:
                    bombs += 1
            elif game['mask'][r][c] == False:
                covered_squares += 1

    if bombs != 0:
        # if bombs is not equal to zero, set the game state to defeat and
        # return 0
        game['state'] = 'defeat'

        return 0

    if covered_squares == 0:
        game['state'] = 'victory'

        return 0

    if not game['mask'][row][col]:
        game['mask'][row][col] = True
        revealed = 1
    else:
        return 0

    if game['board'][row][col] == 0:
        num_rows, num_cols = game['dimensions']

        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                r = row + x
                c = col + y

                if (0 <= r < num_rows) and (0 <= c < num_cols):
                    if (game["board"][r][c] != '.') and (not game["mask"][r][c]):
                        revealed += dig_2d(game, r, c)

    bombs = 0  # set number of bombs to 0
    covered_squares = 0

    for r in range(game['dimensions'][0]):
        for c in range(game['dimensions'][1]):

            if game['board'][r][c] == '.':
                if game['mask'][r][c]:
                    bombs += 1
            elif game['mask'][r][c] == False:
                covered_squares += 1
    bad_squares = bombs + covered_squares

    if bad_squares > 0:
        game['state'] = 'ongoing'
    else:
        game['state'] = 'victory'

    return revealed


def render_2d(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares), '.'

    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring bombs).
    game['mask'] indicates which squares should be visible.  If xray is True (the
    default is False), game['mask'] is ignored and all cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """

    n_rows, n_cols = game["dimensions"]
    result = copy(game["board"])

    for i in range(n_rows):
        for j in range(n_cols):
            if game["mask"][i][j] or xray:
                if game["board"][i][j] == 0:
                    result[i][j] = ' '
                else:
                    result[i][j] = str(game["board"][i][j])
            else:
                result[i][j] = '_'

    return result


def render_ascii(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function 'render_2d(game)'.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> print(render_ascii({'dimensions': (2, 4),
    ...                     'state': 'ongoing',
    ...                     'board': [['.', 3, 1, 0],
    ...                               ['.', '.', 1, 0]],
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """

    res_2d = render_2d(game, xray)

    res = ["".join(row) for row in res_2d]

    result = "\n".join(res)

    return result


# N-D IMPLEMENTATION


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    board = init_array(dimensions, 0)
    mask = init_array(dimensions, False)

    for bomb in bombs:
        assign_value(board, bomb, '.')

    coord_gen = get_coordinates_gen(dimensions)
    rel_neighbor_coords = get_neighbors_relative_coordinates(dimensions)

    for coord in coord_gen:
        if get_value(board, coord) == 0:
            neighbor_bombs = 0
            neighbor_coords = get_neighbors_coordinates(
                coord, rel_neighbor_coords, dimensions)

            for o in neighbor_coords:
                neighbor = get_value(board, o)

                if neighbor == '.':
                    neighbor_bombs += 1
            assign_value(board, coord, neighbor_bombs)

    return {
        'dimensions': dimensions,
        'board': board,
        'mask': mask,
        'state': 'ongoing'}


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """

    if game['state'] == 'defeat' or game['state'] == 'victory':
        return 0

    if get_value(game['board'], coordinates) == '.':
        assign_value(game['mask'], coordinates, True)
        game['state'] = 'defeat'

        return 1

    bombs = 0
    covered_squares = 0

    coord_gen = get_coordinates_gen(game['dimensions'])

    for coord in coord_gen:
        if get_value(game['board'], coord) == '.':
            if get_value(game['mask'], coord):
                bombs += 1
        elif get_value(game['mask'], coord) == False:
            covered_squares += 1

    if bombs != 0:
        game['state'] = 'defeat'

        return 0

    if covered_squares == 0:
        game['state'] = 'victory'

        return 0

    if not get_value(game['mask'], coordinates):
        assign_value(game['mask'], coordinates, True)
        revealed = 1
    else:
        return 0

    if get_value(game['board'], coordinates) == 0:
        rel_neighbor_coords = get_neighbors_relative_coordinates(
            game['dimensions'])
        neighbor_coords = get_neighbors_coordinates(
            coordinates, rel_neighbor_coords, game['dimensions'])

        for o in neighbor_coords:
            neighbor = get_value(game['board'], o)
            neighbor_mask = get_value(game['mask'], o)

            if (neighbor != '.') and (not neighbor_mask):
                revealed += dig_nd(game, o)

    bombs = 0
    covered_squares = 0

    coord_gen = get_coordinates_gen(game['dimensions'])

    for coord in coord_gen:
        if get_value(game['board'], coord) == '.':
            if get_value(game['mask'], coord):
                bombs += 1
        elif get_value(game['mask'], coord) == False:
            covered_squares += 1

    bad_squares = bombs + covered_squares

    if bad_squares > 0:
        game['state'] = 'ongoing'
    else:
        game['state'] = 'victory'

    return revealed


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True], [True, True]],
    ...               [[False, False], [False, False], [True, True], [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    result = copy(game['board'])

    coord_gen = get_coordinates_gen(game['dimensions'])

    for coord in coord_gen:
        if get_value(game['mask'], coord) or xray:
            if get_value(game['board'], coord) == 0:
                assign_value(result, coord, ' ')
            else:
                assign_value(result, coord, str(
                    get_value(game['board'], coord)))
        else:
            assign_value(result, coord, '_')

    return result


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so, comment
    # out the above line, and uncomment the below line of code. This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    #
    #doctest.run_docstring_examples(render_2d, globals(), optionflags=_doctest_flags, verbose=False)
