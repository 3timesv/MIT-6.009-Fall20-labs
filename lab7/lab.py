# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self, value=None):
        self.value = value
        self.children = {}
        self.type = None

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """

        if self.type is None:
            self.type = type(key)

        if type(key) != self.type:
            raise TypeError

        # e.g 'bat'
        first_char = key[:1]  # 'b'
        others = key[1:]  # 'at'

        # if hit last character of key

        if len(first_char) != 0 and len(others) == 0:
            # if not in children, add node and assign value

            if first_char not in self.children:
                node = Trie(value)
                self.children[first_char] = node
                node.type = self.type

            # just assign value
            else:
                node = self.children[first_char]
                node.value = value

        else:
            if first_char not in self.children:
                node = Trie()
                # creat new node for first_char
                self.children[first_char] = node
                node[others] = value  # recurse for others
                node.type = self.type
            else:
                self.children[first_char][others] = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """

        if type(key) != self.type:
            raise TypeError

        first_char = key[:1]
        others = key[1:]

        if first_char not in self.children:
            print("FIRST_CHAR", first_char)
            print("self.children", self.children)
            raise KeyError

        if len(first_char) != 0 and len(others) == 0:
            node = self.children[first_char]

            if node.value is None:
                raise KeyError

            return node.value
        else:
            return self.children[first_char][others]

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """

        if type(key) != self.type:
            raise TypeError

        first_char = key[:1]
        others = key[1:]

        if first_char not in self.children:
            raise KeyError

        if len(first_char) != 0 and len(others) == 0:
            node = self.children[first_char]

            if node.value is None:
                raise KeyError
            node.value = None
        else:
            del self.children[first_char][others]

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        """

        if type(key) != self.type:
            return False

        first_char = key[:1]
        others = key[1:]

        if first_char not in self.children:
            return False

        if len(first_char) != 0 and len(others) == 0:
            node = self.children[first_char]

            if node.value is None:
                return False

            return True
        else:
            return others in self.children[first_char]

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """

        def inner(stack, node):
            if node.value is not None and stack != '' and stack != ():
                yield (stack, node.value)

            for key, child in node.children.items():
                for char, value in inner(stack + key, child):
                    yield (char, value)

        init_stack = ''

        if self.type == tuple:
            init_stack = ()

        return inner(init_stack, self)


def add_freq_trie(keys, trie):
    for key in keys:
        if key in trie:
            trie[key] += 1
        else:
            trie[key] = 1

    return trie


def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    trie = Trie()

    sentences = tokenize_sentences(text)

    for sentence in sentences:
        words = sentence.split()
        add_freq_trie(words, trie)

    return trie


def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    trie = Trie()

    sentences = tokenize_sentences(text)
    tuples = [tuple(sentence.split()) for sentence in sentences]

    add_freq_trie(tuples, trie)

    return trie


def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """

    if type(prefix) != trie.type:
        raise TypeError

    result = []

    if max_count == 0:
        return result

    if prefix in trie:
        result.append((prefix, trie[prefix]))

    for i, elt in enumerate(prefix):
        if isinstance(prefix, tuple):
            elt = (elt,)

        if elt in trie.children:
            trie = trie.children[elt]
        else:
            return result

        if i == len(prefix) - 1:
            break

    for key, _ in trie:
        result.append((prefix + key, trie[key]))

    sorted_result = sorted(result, key=lambda x: x[1], reverse=True)

    if max_count is None or len(result) <= max_count:
        return [key for key, _ in sorted_result]

    return [key for key, _ in sorted_result[:max_count]]


# >>>>> Helper functions for autocorrect

ALPHABETS = "abcdefghijklmnopqrstuvwxyz"


def insert(trie, prefix):
    result = set()
    prefix_list = list(prefix)

    for i in range(len(prefix)):

        for letter in ALPHABETS:
            prefix_list.insert(i, letter)
            new_word = ''.join(prefix_list)

            if new_word in trie:
                result.add(new_word)

            del prefix_list[i]

    return result - set([prefix])


def delete(trie, prefix):
    result = set()
    prefix_list = list(prefix)

    for i, char in enumerate(prefix):
        del prefix_list[i]
        new_word = ''.join(prefix_list)

        if new_word in trie:
            result.add(new_word)

        prefix_list.insert(i, char)

    return result - set([prefix])


def replace(trie, prefix):
    result = set()
    prefix_list = list(prefix)

    for i, char in enumerate(prefix):

        for letter in ALPHABETS:
            prefix_list[i] = letter
            new_word = ''.join(prefix_list)

            if new_word in trie:
                result.add(new_word)
            prefix_list[i] = char

    return result - set([prefix])


def transpose(trie, prefix):
    result = set()
    prefix_list = list(prefix)

    for i in range(1, len(prefix)):

        # swap elements at i and i-1
        prefix_list[i], prefix_list[i-1] = prefix_list[i-1], prefix_list[i]

        new_word = ''.join(prefix_list)

        if new_word in trie:
            result.add(new_word)

        # swap again to get back original state
        prefix_list[i], prefix_list[i-1] = prefix_list[i-1], prefix_list[i]

    return result - set([prefix])


def get_valid_edits(trie, prefix):

    edits = [insert, delete, replace, transpose]

    result = set()

    for edit in edits:
        sub_result = edit(trie, prefix)
        result |= sub_result

    return list(result)


# <<<<<<<<


def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """

    autocompleted = autocomplete(trie, prefix, max_count)

    edits = get_valid_edits(trie, prefix)

    edits_items = [(key, trie[key]) for key in edits]
    sorted_edits_items = sorted(edits_items, key=lambda x: x[1], reverse=True)
    result = [word for word, _ in sorted_edits_items]

    if max_count is None:

        return autocompleted + result

    if len(autocompleted) < max_count:

        return autocompleted + result[:max_count - len(autocompleted)]

    return autocompleted


# >>>>>>>>>> Helpers for word_filter


def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """

    def inner(trie, pattern, stack='', result=set()):

        if pattern == '':
            if trie.value is not None:
                result.add((stack, trie.value))

            return result

        if pattern[0] == '*':
            result |= inner(trie, pattern[1:], stack, result)

        for key, child in trie.children.items():

            if pattern[0] == key or pattern[0] == '?':
                result |= inner(child, pattern[1:], stack+key, result)
            elif pattern[0] == '*':
                result |= inner(child, pattern, stack+key, result)

        return result

    result = inner(trie, pattern)

    return list(result)


# <<<<<<<<<<<<<<<
# you can include test cases of your own in the block below.

if __name__ == '__main__':
    pass
