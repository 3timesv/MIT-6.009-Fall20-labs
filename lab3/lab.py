#!/usr/bin/env python3

import pickle

# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for this lab will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).


KEVIN_BACON = 4724


def transform_data(raw_data):

    new_data = {"a2a": {}, "m2a": {}}

    for actor1, actor2, movie_id in raw_data:
        new_data["a2a"].setdefault(actor1, set()).add(actor2)
        new_data["a2a"].setdefault(actor2, set()).add(actor1)

        new_data["m2a"].setdefault(movie_id, set()).update({actor1, actor2})

    return new_data


def acted_together(data, actor_id_1, actor_id_2):
    if actor_id_1 == actor_id_2:
        return True

    return actor_id_1 in data["a2a"][actor_id_2]


def actors_with_bacon_number(data, n):

    visited = set()
    actors = {KEVIN_BACON}

    if n == 0:
        return actors

    for _ in range(n):

        if len(actors) == 0:
            break

        visited |= actors

        next_actors = set()

        for a in actors:
            next_actors |= data["a2a"][a]

        actors = next_actors - visited

    return actors


def bacon_path(data, actor_id):

    return actor_to_actor_path(data, KEVIN_BACON, actor_id)


def helper_actor_path(data, actor_id_1, goal_function, preds, actor_id_2=None):

    visited = {actor_id_1}
    path = []

    queue = [actor_id_1]

    index = 0

    while index < len(queue):
        curr = queue[index]

        if goal_function(curr):
            if actor_id_2 is None:
                actor_id_2 = curr
            break

        for n in data["a2a"][curr] - visited:
            preds[n] = curr
            queue.append(n)
            visited.add(n)
        index += 1

    if preds.setdefault(actor_id_2, None) is not None:
        path = [actor_id_2]
        pred = preds[actor_id_2]

        while pred is not actor_id_1:
            path.append(pred)
            pred = preds[pred]
        path.append(actor_id_1)
        path.reverse()

        return path

    return None

def actor_to_actor_path(data, actor_id_1, actor_id_2):
    preds = {actor_id_2: None}

    def goal(actor):
        return actor == actor_id_2

    return helper_actor_path(data, actor_id_1, goal, preds, actor_id_2)

def actor_path(data, actor_id_1, goal_test_function):
    if goal_test_function(actor_id_1):
        return [actor_id_1]

    preds = {}

    return helper_actor_path(data, actor_id_1, goal_test_function, preds)


def actors_connecting_films(data, film1, film2):

    film1_actors = data["m2a"][film1]
    film2_actors = data["m2a"][film2]

    paths = []

    for actor1 in film1_actors:
        for actor2 in film2_actors:
            path = actor_to_actor_path(data, actor1, actor2)

            if path is not None:
                paths.append(path)

    min_path_idx = 0

    for i in range(len(paths)):
        if len(paths[i]) < len(paths[min_path_idx]):
            min_path_idx = i

    return paths[min_path_idx]


if __name__ == '__main__':
    with open('resources/small.pickle', 'rb') as f:
        smalldb = pickle.load(f)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    with open("resources/tiny.pickle", "rb") as f:
        tinydb = pickle.load(f)

    print("tinydb", tinydb)

    print("transformed tinydb", transform_data(tinydb))
    res = bacon_path(transform_data(tinydb), 1560)

    import pdb
    pdb.set_trace()

    with open("resources/large.pickle", "rb") as f:
        largedb = pickle.load(f)
    res2 = bacon_path(transform_data(largedb), 1240)

    """ 2.2
    with open("resources/names.pickle", "rb") as f:
        namesdb = pickle.load(f)
    print(type(namesdb))
    print(namesdb["Julian O'Donnell"])
    for n in namesdb:
        if namesdb[n] == 1:
            print(n)
    """
