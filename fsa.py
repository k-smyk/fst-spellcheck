#!/usr/bin/env python3
"""
Data Structures and Algorithms for CL 3, Project 1
See <https://https://dsacl3-2022.github.io/p1/> for detailed instructions.
Author:      Pun Ching Nei, Lorena Raichle, Kateryna Smykovska
Honor Code:  I pledge that this program represents my work.
We received help from: no one in designing and debugging our program.
"""
import re

class FSA:
    """ A class representing finite state automata.
    Args:
        deterministic: The automaton is deterministic
    Attributtes:
        transitions: transitions kept as a dictionary
            where keys are the tuple (source_state, symbol),
            values are the target state for DFA
            and a set of target states for NFA.
            Note that we do not require a dedicated 'sink' state.
            Any undefined transition should cause the FSA to reject the
            string immediately.
        start_state: number/name of the start state
        accepting: the set of accepting states
        is_deterministic (boolean): whether the FSA is deterministic or not
    """

    def __init__(self, deterministic=True):
        self.transitions = dict()
        self.start_state = None
        self.accepting = set()
        self.is_deterministic = deterministic
        self._alphabet = set()  # just for convenience, we can
        self._states = set()  # always read it off from transitions

    def add_transition(self, s1, sym, s2=None, accepting=False):
        """ Add an transition from state s1 to s2 with symbol
        """
        if self.start_state is None:
            self.start_state = s1
            self._states.add(s1)
        if s2 is None:
            s2 = len(self._states)
            while s2 in self._states: s2 += 1
        self._states.add(s2)
        self._alphabet.add(sym)
        if (s1, sym) not in self.transitions:
            self.transitions[(s1, sym)] = set()
        self.transitions[(s1, sym)].add(s2)
        if accepting:
            self.accepting.add(s2)
        if len(self.transitions[(s1, sym)]) > 1:
            self.is_deterministic = False
        return s2

    def mark_accept(self, state):
        self.accepting.add(state)

    def is_accepting(self, state):
        return state in self.accepting

    def move(self, sym, s1=None):
        """ Return the state(s) reachable from 's1' on 'symbol'
        """
        if s1 is None: s1 = self.start_state
        if (s1, sym) not in self.transitions:
            return None
        else:
            return self.transitions[(s1, sym)]

    def _recognize_dfa(self, s):
        state = self.start_state
        for sym in s:
            states = self.transitions.get((state, sym), None)
            if states is None:
                return False
            else:
                state = next(iter(states))
        if state in self.accepting:
            return True
        else:
            return False

    def _recognize_nfa(self, s):
        """ NFA recognition of 's' using a stack-based agenda.
        """
        agenda = []
        state = self.start_state
        inp_pos = 0
        for node in self.transitions.get((self.start_state, s[inp_pos]), []):
            agenda.append((node, inp_pos + 1))
        while agenda:
            node, inp_pos = agenda.pop()
            if inp_pos == len(s):
                if node in self.accepting:
                    return True
            else:
                for node in self.transitions.get((node, s[inp_pos]), []):
                    agenda.append((node, inp_pos + 1))
        return False

    def recognize(self, s):
        """ Recognize the given string 's', return a boolean value
        """
        if self.is_deterministic:
            return self._recognize_dfa(s)
        else:
            return self._recognize_nfa(s)

    def minimize(self):
        """ Minimize the automaton.

        You are free to use any of the minimization algorithms here.
        """
        # minimization by partitioning
        # construct a set of accepting and non-accepting states (0 equivalence)
        transitions = m.transitions
        print(transitions)
        input_list = []
        for item in m.transitions.keys():
            if item[1] not in input_list:
                input_list.append(item[1])
        print(input_list)
        accepting_states = set()  # final set of accepting states
        non_accepting_states = set()
        accept = m.accepting
        # convert set of accepting states
        for element in accept:
            if isinstance(element, int):
                accepting_states.add(element)
            elif isinstance(element, frozenset) or isinstance(element, set):
                for sub_element in element:
                    if isinstance(sub_element, int):
                        accepting_states.add(sub_element)
        for i in range(max(accepting_states)):
            if i not in accepting_states:
                non_accepting_states.add(i)
        # print("accepting states:")
        # print(accepting_states)
        # print("non accepting")
        # print(non_accepting_states)

        # 1 equivalence: check (first for non-accepting states: 0 and 1 with all possible inputs -> result in same set?)
        list_accept = list(accepting_states)
        list_non_accept = list(non_accepting_states)
        dict_sets = []  # states that are not in the same set
        input_idx = 0
        # check for all possible inputs
        while input_idx < len(input_list):
            i = 0  # to get node (item 1) from sets
            j = 1
            # check for all non-accepting states
            while j < len(list_non_accept):
                set_non_accepting_1 = False
                set_accepting_1 = False
                set_non_accepting_2 = False
                set_accepting_2 = False
                # compare item by item from set of non-accepting states
                item1 = list_non_accept[i]
                item2 = list_non_accept[j]
                res_item1 = 0
                res_item2 = 0
                # check in which set the ending state is for the respective input (for item 1) (0-w)
                input = input_list[input_idx]
                if (item1, input) not in m.transitions.keys():  # if not in dict...
                    res_item1 = item1  # ... state stays same
                else:  # if in dict...
                    res_item1 = m.transitions[(item1, input)]
                    res_item1 = int(list(res_item1)[0])
                # ... check if ending state is in accepting / non-accepting set and update variable
                if res_item1 in non_accepting_states:
                    set_non_accepting_1 = True
                else:
                    set_accepting_1 = True
                # check in which set the ending state is for the respective input (for item 2) (1-w)
                if (item2, input) not in m.transitions.keys():  # if not in dict...
                    res_item2 = item2  # ... state stays same
                else:  # if in dict...
                    res_item2 = m.transitions[(item2, input)]
                    res_item2 = int(list(res_item2)[0])
                # ... check if ending state is in accepting / non-accepting set and update variable
                if res_item2 in non_accepting_states:
                    set_non_accepting_2 = True
                else:
                    set_accepting_2 = True
                # print("same set?")
                # check if item 1 and item 2 are in the same set or in different sets
                if set_non_accepting_1 and set_non_accepting_2 or set_accepting_1 and set_accepting_2:
                    print(str(list_non_accept[i]) + " and " + str(
                        list_non_accept[j]) + " are in same set!" + " for input: " + input)
                else:
                    if item1 not in dict_sets:
                        dict_sets.append(item1)
                    if item2 not in dict_sets:
                        dict_sets.append(item2)
                    # print(str(list_non_accept[i]) + " and " + str(
                    #     list_non_accept[j]) + " are NOT in same set!" + " for input: " + input)
                # check for similarity in sets
                # k = 0
                # l= 1
                # if len(dict_sets) >= 2 and l <= len(dict_sets):
                #     listing = []
                #     if dict_sets[k] and dict_sets[l] not in list_non_accept:
                #         if dict_sets[k] and dict_sets[l] not in list_accept:
                #             listing = [dict_sets[l]]
                #             dict_sets.append(listing)
                #     k += 1
                #     l += 1
                # print(dict_sets)

                # next item
                j += 1
            # next input
            input_idx += 1
        # print("reduction of the following states: ")
        # print(dict_sets)
        # reduction of the states in the trie
        min_trie = FSA(deterministic=True)
        for key in m.transitions.keys():
            if key[0] not in dict_sets:
                sym = m.transitions[(key[0], key[1])]
                sym = int(list(sym)[0])
                min_trie.add_transition(key[0], key[1], sym)
                if sym in accepting_states:
                    min_trie.mark_accept(sym)
        # print(min_trie.transitions)
        return min_trie


def build_trie(words):
    """Given a list of words, create and return a trie FSA.

    For the given sequence of words, you should build a trie,
    an FSA where letters are the edge labels. Since the structure is a
    trie, common prefix paths should be shared but suffixes will
    necessarily use many redundant paths.

    You should initialize an instance of the FSA class defined above,
    and add only the required arcs successively.
    """
    my_trie = FSA(deterministic=True)
    # TO DELETE:
    transitions = my_trie.transitions
    node_count = 0  # (node count = character position in word)
    my_trie.start_state = node_count
    sorted_words = sorted(words, key=len,
                          reverse=True)  # sorted list from longest to shortest string to insert into trie
    real_node = len(sorted_words[0])  # keep track of the (ordered) number of nodes in the trie
    dict_tokens = {}  # dict to keep track of each token with it's last node count of the row / keep track of stem (longest word first inserted)
    prev_token = ""  # keep track of previously processed token of list
    for token in sorted_words:  # process word by word, character by character
        new_string = False
        for char in token:
            # if input is not in transitions dict / trie...
            if (node_count, char) not in my_trie.transitions or new_string:
                last_word_length = len(sorted_words[0])  # word length of last token
                if len(token) < last_word_length:  # if token length smaller, reaching a side branch of the trie...
                    last_word_length = len(token)
                    node_count = dict_tokens[prev_token] + 1  # ... therefore adapt node_count
            # check again (aslo for updated node count if side branch of trie is reached) if already in trie
            if (node_count, char) not in my_trie.transitions or new_string:
                tmp = list(my_trie.transitions.keys())
                res = [x for x, _ in tmp]  # list of node counts
                # check if node_count is already in dict but with another character
                # -> a new transition + node has to be added after the last node
                if node_count in res:
                    # connect to last node of new string
                    if new_string:
                        my_trie.add_transition(len(res), char, len(res) + 1, accepting=False)
                        node_count += 1
                    else:
                        # connect to node count
                        my_trie.add_transition(node_count, char, len(res) + 1, accepting=False)
                        node_count += 1
                        new_string = True  # a new string (and not only a prefix-string) is inserted to the trie
                else:  # if node_count did not appear in the node count list (res), add
                    my_trie.add_transition(node_count, char, len(res) + 1, accepting=False)
                    node_count += 1
                    new_string = True
                    # dict to keep track of stem
                    dict_tokens[char] = node_count  # add current char and node count to dict
            else:  # if char in string / if already in dict
                node_count += 1

        # if char is at last position of string, mark as accepting state
        if char is token[-1]:
            if new_string:  # whole string (last) walks, walls, wants, works, forks
                my_trie.mark_accept(len(res) + 1)
                last_accepting = (len(res) + 1)
            elif real_node > len(sorted_words[0]):  # prefix string: walk, wall, want
                mark = my_trie.transitions[(node_count - 1, token[-1])]
                my_trie.mark_accept(frozenset(mark))
                for item in frozenset(mark):
                    last_accepting = item
            # update the count in dict_token (to achieve correct accepting state for prefix strings already in trie)
            dict_tokens[token] = last_accepting
            keys = dict_tokens.keys()
            key = ""
            for token in keys:
                key += token + " "
            if len(token) < len(sorted_words[0]):
                match = re.search(token, key)
                if match:
                    start_index = match.start()
                    end_index = key.find(" ", start_index)
                    word = key[start_index:end_index]
                    res = dict_tokens[word]
                    dict_tokens[token] = res

        real_node += 1
        prev_token = token
        node_count = 0
    accept = my_trie.accepting
    # convert set of accepting states
    int_set = set()  # final set of accepting states
    for element in accept:
        if isinstance(element, int):
            int_set.add(element)
        elif isinstance(element, frozenset) or isinstance(element, set):
            for sub_element in element:
                if isinstance(sub_element, int):
                    int_set.add(sub_element)

    return my_trie


if __name__ == '__main__':
    # Example usage:
    m = build_trie(["walk", "walks", "wall", "walls", "want", "wants",
                    "work", "works", "forks"])
    m.write("m_try")
    m.minimize().write("minimize")
    # assert m.recognize("walk") == True
    # assert m.recognize("wark") == False
