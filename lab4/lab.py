#!/usr/bin/env python3

from util import great_circle_distance, read_osm_data, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)
    """

    # nodes: dict - {node_id : {ways: (list), lat: (float), lon: (float)}}
    # ways: dict - {way_id : {nodes: (list), oneway: (bool), maxspeed_mph: (int)}}
    nodes = {}
    ways = {}

    for way in read_osm_data(ways_filename):
        if "highway" in way["tags"]:

            if way["tags"]["highway"] in ALLOWED_HIGHWAY_TYPES:

                ways[way["id"]] = {"nodes": way["nodes"]}

                if way["tags"].get("oneway", "no") == "no":
                    ways[way["id"]]["oneway"] = False
                else:
                    ways[way["id"]]["oneway"] = True

                ways[way["id"]]["maxspeed_mph"] = way["tags"].get(
                    "maxspeed_mph", DEFAULT_SPEED_LIMIT_MPH[way["tags"]["highway"]])

                # append way on which node is present

                for node in way["nodes"]:
                    nodes.setdefault(node, {}).setdefault(
                        "ways", []).append(way["id"])

    for node in read_osm_data(nodes_filename):
        # only use nodes which are on some way

        if node["id"] in nodes:
            nodes[node["id"]]["lat"] = node["lat"]
            nodes[node["id"]]["lon"] = node["lon"]

    return nodes, ways


def get_children(node, aux_structures):
    """
    Get children (nodes adjacent) of given node.

    Parameters:
        node: given node
        aux_structures: result of calling build_auxiliary_structures

    Returns:
        dictionary of children with values as maxspeed_mph from node to child.
    """
    nodes, ways = aux_structures

    children = {}

    def add_child(idx, way_id):
        child = ways[way_id]["nodes"][idx]
        speed = ways[way_id]["maxspeed_mph"]

        if (child not in children) or (child in children and children[child] < speed):
            children[child] = speed

    # ways at which given node is present
    neighbor_ways = nodes[node]["ways"]

    for way_id in neighbor_ways:
        # append next node to children if it exists
        nxt_idx = ways[way_id]["nodes"].index(node) + 1

        if nxt_idx < len(ways[way_id]["nodes"]):
            add_child(nxt_idx, way_id)

        # append previous node to children if path is not oneway

        if not ways[way_id]["oneway"]:

            prev_idx = ways[way_id]["nodes"].index(node) - 1

            if prev_idx >= 0:
                add_child(prev_idx, way_id)

    return children


def compute_distance(node1, node2, aux_structures):
    """
    Compute distance between two given nodes

    Parameters:
        node1: start node
        node2: end node
        aux_structures: the result of calling build_axiliary_structures

    Returns:
        (float) distance b/w node1 and node2
    """
    nodes, _ = aux_structures
    loc1 = (nodes[node1]["lat"], nodes[node1]["lon"])
    loc2 = (nodes[node2]["lat"], nodes[node2]["lon"])

    dist = great_circle_distance(loc1, loc2)

    return dist


def compute_time(node1, node2, aux_structures, children):
    """
    Compute time to travel from start to end node

    Parameters:
        node1: start node
        node2: end node
        aux_structures: the result of calling build_axiliary_structures

    Returns:
        (float) time to go from node1 to node2
    """

    dist = compute_distance(node1, node2, aux_structures)
    speed = children[node2]

    time = dist / speed

    return time


def sort_by_cost(aux_structures, agenda, node2, heuristic=False):
    """
    Sorts given agenda by cost.

    Parameters:
        aux_structures: result of calling build_aux_structures
        agenda: given list to sort
        node2: goal node
        heuristic: if True, uses heuristic + cost as total cost for sorting

    Returns:
        new sorted list.
    """

    if not heuristic:
        return sorted(agenda, key=lambda x: x[0])

    def h(node1, node2):
        return compute_distance(node1, node2, aux_structures)

    return sorted(agenda, key=lambda x: x[0] + h(x[1], node2))


def find_path_nodes(aux_structures, node1, node2, cost_function):
    """
    Return the least costly path between the two nodes

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the least costly path (in terms of
        distance) from node1 to node2
    """
    expanded = set()
    agenda = [(0, node1, [node1])]

    while len(agenda) != 0:
        # pop lowest cost path from agenda
        cost, node, path = sort_by_cost(
            aux_structures, agenda, node2, False)[0]
        del agenda[agenda.index((cost, node, path))]

        if node in expanded:
            continue

        # return path if current node is goal

        if node == node2:
            return path
        # else ready to expand it
        expanded.add(node)

        children = get_children(node, aux_structures)

        for child in children:
            if child not in expanded:
                if cost_function == compute_distance:
                    add_cost = cost_function(node, child, aux_structures)
                else:
                    add_cost = cost_function(
                        node, child, aux_structures, children)
                new_path = path.copy() + [child]
                new_cost = cost + add_cost
                agenda.append((new_cost, child, new_path))


def find_short_path_nodes(aux_structures, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """

    return find_path_nodes(aux_structures, node1, node2, compute_distance)


def nearest_nodes(aux_structures, *locs):
    """
    Find nearest nodes to given locations respectively.

    Parameters:
        aux_structures: result of calling build_auxiliary_structures
        *locs: given locations

    Returns:
        list of nearest nodes.
    """

    nodes, _ = aux_structures

    nearest = {loc: {"node": None, "dist": 1e10} for loc in locs}

    for node in nodes:
        loc2 = (nodes[node]["lat"], nodes[node]["lon"])

        for loc1 in nearest:
            dist = great_circle_distance(loc1, loc2)

            if dist < nearest[loc1]["dist"]:
                nearest[loc1]["dist"] = dist
                nearest[loc1]["node"] = node

    return [nearest[loc]["node"] for loc in nearest.keys()]


def nodes_to_locs(aux_structures, nodes_id):
    """
    Get GPS locations of given nodes.

    Parameters:
        aux_structures: result of calling build_auxiliary_structures
        nodes: list of nodes

    Returns:
        list of locations
    """

    nodes, _ = aux_structures
    locs = [(nodes[n]["lat"], nodes[n]["lon"]) for n in nodes_id]

    return locs


def find_path(aux_structures, loc1, loc2, cost_function):
    """
    Return the least costly path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the
        least costly path from loc1 to loc2.
    """
    n1, n2 = nearest_nodes(aux_structures, loc1, loc2)
    short_path_nodes = find_path_nodes(aux_structures, n1, n2, cost_function)

    if short_path_nodes is not None:
        short_path_locs = nodes_to_locs(aux_structures, short_path_nodes)

        return short_path_locs


def find_short_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """

    return find_path(aux_structures, loc1, loc2, compute_distance)


def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """

    return find_path(aux_structures, loc1, loc2, compute_time)


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    mit_nodes = "resources/mit.nodes"
    mit_ways = "resources/mit.ways"

    aux_data = build_auxiliary_structures(mit_nodes, mit_ways)

    import pdb
    pdb.set_trace()

    loc1 = (42.3603, -71.095)  # near Building 35
    loc2 = (42.3573, -71.0928)  # Near South Maseeh
    expected_path = [
        (42.3601, -71.0952), (42.3592, -71.0932),
        (42.3582, -71.0931), (42.3575, -71.0927),
    ]

    res = find_short_path(aux_data, loc1, loc2)

    """
    # 2.1
    print("2.1 started...")

    cam_nodes = "resources/cambridge.nodes"
    cam_ways = "resources/cambridge.ways"

    sum_nodes = 0
    sum_names = 0

    for node in read_osm_data(cam_nodes):
        sum_nodes += 1

        if "name" in node["tags"]:
            sum_names += 1

            if node["tags"]["name"] == "77 Massachusetts Ave":
                id_num = node["id"]

    print("Total nodes:", sum_nodes)
    print("Total nodes having name:", sum_names)
    print("ID number of node named '77 Massachusetts Ave':", id_num)

    sum_ways = 0
    sum_oneways = 0

    for way in read_osm_data(cam_ways):
        sum_ways += 1

        if "oneway" in way["tags"]:
            sum_oneways += 1

    print("Total ways:", sum_ways)
    print("Total oneways:", sum_oneways)

    print("2.1 finished.")

    # 3.1.3
    print("3.1.3 started...")

    loc1 = (42.363745, -71.100999)
    loc2 = (42.361283, -71.239677)
    dist1 = great_circle_distance(loc1, loc2)
    print("Distance 1:", dist1)

    midwest_nodes = "resources/midwest.nodes"
    midwest_ways = "resources/midwest.ways"
    id1 = 233941454
    id2 = 233947199

    for node in read_osm_data(midwest_nodes):
        if node["id"] == id1:
            node1 = node
        elif node["id"] == id2:
            node2 = node

    loc1 = (node1["lat"], node1["lon"])
    loc2 = (node2["lat"], node2["lon"])
    dist2 = great_circle_distance(loc1, loc2)
    print("Distance 2:", dist2)

    way_id = 21705939

    for way in read_osm_data(midwest_ways):
        if way["id"] == way_id:
            my_way = way

            break

    nodes_locs = []

    for node in read_osm_data(midwest_nodes):
        if node["id"] in my_way["nodes"]:
            nodes_locs.append((node["lat"], node["lon"]))
            my_way["nodes"].remove(node["id"])

        if len(my_way["nodes"]) == 0:
            break

    sum_dist = 0.0
    loc1 = None

    for loc in nodes_locs:
        if loc1 is None:
            loc1 = loc

            continue
        else:
            loc2 = loc

        dist = great_circle_distance(loc1, loc2)
        sum_dist += dist

        loc1 = loc2
    print("Length of way:", sum_dist)

    print("3.1.3 finished.")
    """
