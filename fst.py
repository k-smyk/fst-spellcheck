#!/usr/bin/env python3
"""
Data Structures and Algorithms for CL 3, Project 1
See <https://https://dsacl3-2022.github.io/p1/> for detailed instructions.
Author:      Pun Ching Nei, Lorena Raichle, Kateryna Smykovska
Honor Code:  I pledge that this program represents my work.
We received help from: no one in designing and debugging our program.
"""


class FST:
    """A weighted FST class.
    """

    def __init__(self):
        self.transitions = dict()
        self.start_state = None
        self.accepting = set()
        self._sigma_in = set()
        self._sigma_out = set()
        self._states = set([0])

    @classmethod
    def fromfsa(cls, fsa):
        """Return an FST instance using an FSA.

        This method should take an instance of the FSA class defined
        in fsa.py, and returns an FST with identity transitions.
        """
        fst = cls()
        for (s1, sym), s2s in fsa.transitions.items():
            for s2 in s2s:
                fst.add_transition(s1, sym, s2, sym)
        fst.accepting = fsa.accepting
        fst.start_state = fsa.start_state
        return fst

    def mark_accepting(self, state):
        self.accepting.add(state)

    def get_transitions(self, s1, insym=None):
        """
        """
        if insym is None:
            syms = self._sigma_in
        else:
            syms = (insym,)
        for sym in syms:
            if (s1, sym) in self.transitions:
                for outsym, s2, w in self.transitions[(s1, sym)]:
                    yield s2, outsym, w

    def add_transition(self, s1, insym,
                       s2=None, outsym=None, w=0, accepting=False):
        """Add a transition from s1 to s2 with label insym:outsym.

        If s2 is None, create a new state. If outsym is None, assume
        identity transition.

        We assume transition labels are characters, and the states are
        integers, and we use integer labels when we create states.
        However, the code should (mostly) work fine with arbitrary labels.
        """
        if self.start_state is None:
            self.start_state = s1
            self._states.add(s1)
        if s2 is None:
            s2 = len(self._states)
            while s2 in self._states: s2 += 1
        if s2 not in self._states:
            self._states.add(s2)
        if outsym is None: outsym = insym
        self._sigma_in.add(insym)
        self._sigma_out.add(outsym)
        if (s1, insym) not in self.transitions:
            self.transitions[(s1, insym)] = set()
        self.transitions[s1, insym].add((outsym, s2, w))
        if accepting:
            self.accepting.add(s2)
        return s2

    def move(self, s1, insym):
        """ Return the state(s) reachable from 's1' on 'symbol'
        """
        if (s1, insym) in self.transitions:
            return self.transitions[(s1, insym)]
        else:
            return set()

    def transduce(self, s):
        """ Transduce the string s, returning the result of the transduction.

        You do not need to handle epsilon loops (our FSTs do not have
        epsilon loops).

        Each result should be accompanied by the weight of the
        particular transduction of the input string. We calculate
        the weight of a path as the sum of the weights of the transitions
        in the path (this works well with log probabilities).

        Your method should preferably yield pairs of (output, weight)
        or return a sequence of such pairs.

        Tips:
            - You may find the _recognize_nfa method of the FSA class
              a useful starting point for implementing this method.
            - You will need to keep the output string built so far
              and its weight in your agenda so that you can use it
              when backtracking.
            - Unlike NFA recognition, we cannot stop as soon as we find
              an acceptable string. We want to generate all possible
              paths.
        """
        def recursive_transduce(input_string, current_state, output_string, output_string_container, total_weight):

            if input_string == "" and current_state in self.accepting: # base case
                output_string_container.append((output_string, total_weight))
            if (current_state, input_string[:1]) in self.transitions: # get the path for each value of the key
                for value in self.transitions[(current_state, input_string[:1])]: # save each part of output
                    output_string += value[0]
                    next_state = value[1]
                    total_weight += value[2]
                    recursive_transduce(input_string[1:], next_state, output_string, output_string_container, total_weight)
                    if value[0] != "":  # not deleting the first character while back-tracking
                        output_string = output_string[:-1]
                    total_weight -= value[2] # subtract the weight while back-tracking
            if input_string[:1] != "" and (current_state, "") in self.transitions: # deal with case that the input string is epsilon
                for value in self.transitions[(current_state, "")]:# save each part of output
                    output_string += value[0]
                    next_state = value[1]
                    total_weight += value[2]
                    recursive_transduce(input_string, next_state, output_string, output_string_container, total_weight)
                    if value[0] != "": # not deleting the first character while back-tracking
                        output_string = output_string[:-1]
                    total_weight -= value[2] # subtract the weight while back-tracking

        container = []
        recursive_transduce(s, self.start_state, "", container, 0)
        return container

    def invert(self):
        """Invert the FST.
        """
        invert_fst = FST()

        # mark the accepting state of the inverted version
        invert_fst.accepting = self.accepting
        # invert_fst._sigma_in = self._sigma_out
        # invert_fst._sigma_out = self._sigma_out

        # exchange the s1 and s2 place to invert the fst
        for (s1, insym), s2_total in self.transitions.items():
            for outsym, s2, w in s2_total:
                invert_fst.add_transition(s2, outsym, s1, insym, w)

        self.__dict__ = invert_fst.__dict__



    @classmethod
    def compose_fst(cls, m1, m2):
        """Compose two FST instances (m1 and m2) and return the composed FST.

        While implementing this method, you should pay attention to
        epsilons, since our use case requires epsilon transitions.
        However, you can make use of the fact that `m1` does not
        include any epsilon transitions in our application. Also,
        since `m1` in our application is not weighted, the arc weight
        can trivially be taken from `m2`.
        """
        compose = FST()
        start_state1 = m1.start_state
        start_state2 = m2.start_state
        sigmain1 = m1._sigma_in

        # make the start state
        new_start_state = (start_state1, start_state2)
        compose.start_state = new_start_state

        agenda = [new_start_state]
        visited = set()

        # start to do compose
        while agenda:
            temp = agenda.pop()
            visited.add(temp)
            # looping all pairs of transitions (non-epsilon part)
            for y in sigmain1:
                if (temp[0], y) in m1.transitions and (temp[1], y) in m2.transitions:
                    # loop all possible answer in m1
                    for path1, state1, weight1 in m1.transitions[temp[0], y]:
                        # loop all possible answer in m2
                        for path2, state2, weight2 in m2.transitions[temp[1], path1]:
                            # add transition for the pairs
                            end_state = False
                            if state1 in m1.accepting and state2 in m2.accepting:
                                end_state = True
                            compose.add_transition(temp, y, (state1, state2), path2, weight2, accepting=end_state)
                            # add pair to agenda if it is not in visited
                            if (state1, state2) not in visited:
                                agenda.append((state1, state2))
            # looping all pairs of transitions (epsilon part)
            # if the pair of m2 transition is empty string
            if (temp[1], "") in m2.transitions:
                # starting state
                state1 = temp[0]
                for path2, state2, weight2 in m2.transitions[(temp[1], "")]:
                    # add transition for the pairs
                    end_state = False
                    if state1 in m1.accepting and state2 in m2.accepting:
                        end_state = True
                    compose.add_transition(temp, "", (state1, state2), path2, weight2, accepting=end_state)
                    # add pair to agenda if it is not in visited
                    if (state1, state2) not in visited:
                        agenda.append((state1, state2))

        return compose


if __name__ == "__main__":
    cat = FST()
    cat.add_transition(0,"c",1,"b")
    cat.add_transition(0, "c", 1, "r")
    cat.add_transition(1,"a", 2,"a")
    cat.add_transition(2,"t", 3, "t", accepting=True)
    cat.add_transition(3,"", 4,"s", accepting=True)
    # print(cat.transitions)
    cat.write("normal")
    cat.invert().write("invert")


    # abcd = FST()
    # abcd.add_transition(0, "a", 1, "a")
    # abcd.add_transition(1, "a", 2, "")
    # abcd.add_transition(2, "a", 3, "")
    # abcd.add_transition(3, "c", 4, "c", accepting=True)
    # abcd.add_transition(1, "a", 5, "b")
    # abcd.add_transition(5, "a", 6, "c")
    # abcd.add_transition(6, "a", 7, "d", accepting=True)
    # abcd.invert()

    # abcd.write("abcd")
    # print(abcd.transitions)
    # print(abcd.transduce("aaaa"))

    # print(cat.transduce("cat"))
    # print(cat.transitions)

    # m1 = FST()
    # m1.add_transition(0, "a", 1, "a")
    # m1.add_transition(1, "a", 2, "a", accepting=True)
    # m1.write("m1")
    # print(m1.transitions)
    #
    # m2 = FST()
    # m2.add_transition(0, "a", 0, "a")
    # m2.add_transition(0, "b", 0, "b")
    # m2.add_transition(0, "a", 1, "b")
    # m2.add_transition(0, "b", 1, "a")
    # m2.add_transition(0, "", 1, "b")
    # m2.add_transition(0, "", 1, "a")
    # m2.add_transition(0, "a", 1, "")
    # m2.add_transition(0, "b", 1, "")
    # m2.add_transition(1, "a", 1, "a")
    # m2.add_transition(1, "b", 1, "b", accepting=True)
    # m2.write("m2")
    # print(m2.transitions)

    # test_compose = FST().compose_fst(m1, m2)
    #  print(test_compose.compose_fst(m1, m2).transitions)
    # test_compose.write("compose")

    m1 = FST()
    m2 = FST()

    m1.add_transition(0, "a", 1, "b", 0)
    m1.add_transition(1, "a", 1, "a", 0)
    m1.add_transition(1, "b", 1, "b", 0)
    m1.add_transition(1, "a", 2, "b", 0)
    m1.start_state = 0
    m1.mark_accepting(2)
    # m1.write("m1")

    m2.add_transition(0, "b", 0, "b", 0)
    m2.add_transition(0, "c", 0, "c", 0)
    m2.add_transition(0, "a", 1, "a", 0)
    m2.add_transition(1, "a", 1, "a", 0)
    m2.add_transition(1, "c", 0, "c", 0)
    m2.add_transition(1, "b", 0, "c", 0)
    m2.mark_accepting(0)
    m2.mark_accepting(1)
    # m2.write("m2")

    test_compose = FST().compose_fst(m1, m2)
    # test_compose.write("compose")

