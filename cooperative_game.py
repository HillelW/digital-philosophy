'''
   converts a bankruptcy prolem into a 
   corresponding cooperative game of transferable utility.

   see Aumann and Maschler's 1985 paper: 
   "Game Theoretic Analysis of a Bankruptcy Problem from the Talmud."
'''

from itertools import chain, combinations, permutations
from typing import Callable, List, Tuple


class CooperativeGame (object):
    '''represents a cooperative game'''
    def __init__ (self, num_players: int=None, valuation: dict=None):
        '''
           given a number of players and a valuation function encoded as a dictionary,
           creates an object representing the corresponding cooperative game.

           the valuation function `v` is a set function defined on the powerset
           of a set A which must satisfy the following properties:

           1. v(∅) = 0 - valuation of the empty set is zero,
           2. v(S) ≥ 0 - valuation of each subset must be non-negative,
           3. if S1 ⊂ S2, then v(S1) ≤ v (S2) - valuation function is monotonic.

           The value v(S) represents the value that the coalition S can obtain 
           regardless of what other players do.

           Example Usage:

           v = {
                (1, 2): 100,
                (1, 3): 100,
                (2, 3): 50,
                (1, 2, 3): 120,
                (1, ): 0,
                (2, ): 0, 
                (3, ): 0,
                (): 0
           }
           num_players = 2
           game = CooperativeGame (num_players=3, valuation=v)
        '''
        # verify that we are dealing with a valid cooperative game
        if not isinstance (valuation, dict):
            raise TypeError ("valuation function must be a dictionary!")

        for key in list (valuation):
            if len(str(key)) == 1 and not isinstance(key, tuple):
                valuation[(key,)] = valuation.pop(key)

            elif not isinstance (key, tuple):
                raise TypeError ("key must be a tuple!")

        for key in list (valuation):
            sortedkey = tuple(sorted(key))
            valuation[sortedkey] = valuation.pop (key)

        player_list = max (valuation, key=len)
        for coalition in self.get_powerset (player_list):
            if tuple (sorted(coalition)) not in valuation:
                raise ValueError ("valuation function must be defined on the power set!")

            if not self.empty_set_is_mapped_to_zero (valuation):
                raise ValueError ("empty set must be mapped to zero!")

        self.num_players = num_players
        self.valuation = valuation

    ######################
    # VALIDATION METHODS #
    ######################

    def empty_set_is_mapped_to_zero (self, valuation): 
        return valuation[()] == 0   

    def players_are_mapped_to_greater_than_or_equal_to_zero (self):
        players = tuple (range (1, self.num_players+1))
        return self.valuation[players] >= 0

    def is_monotonic_set_function (self) -> bool:
        '''returns True if the valuation function is monotonic, False otherwise.'''
        v = self.valuation
        set_pairs = permutations (v.keys(), 2)
        for p1, p2 in set_pairs:
            if set (p1) <= set (p2) and v[p1] > v[p2]:
                return False
        return True

    ################
    # GAME METHODS #
    ################
    
    def allocation_problem_to_game (self, claims: List[float], estate: float):
        '''
           given an allocation problem, returns the correspoding game.

           Example Usage:

           game.allocation_problem_to_game ([100, 200, 300], 200 == CooperativeGame (2, {(1,): 0, (2,): 100, (1,2):100})
        '''
        num_players = len (claims)
        players = list (range (1, num_players+1))
        mapping = dict (zip (claims, players))
        powerset = self.get_powerset (claims)
        powerset.remove (())
        
        v = {}

        for subset in powerset:
            complement = list(set (claims) - set (subset))
            sum_of_complement = sum (complement)
            remaining = max (0, estate - sum_of_complement)
            key = []
            for x in subset:
                player = mapping[x]
                key.append (player)
            tup = tuple (key)

            v[tup] = remaining
            v[()] = 0
        return CooperativeGame (num_players=num_players, valuation=v)


    ##################
    # HELPER METHODS #
    ##################

    def get_powerset (self, iterable) -> List[Tuple]:
        '''
           given an iterable, returns the powerset of that iterable.

           Example Usage:
   
           powerset ([1,2,3]) == [() (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)]
        '''
        s = list(iterable)
        return list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))

    def __str__ (self):
        return 'num_players = ' + str (self.num_players) + ',\nvaluation = ' + str (self.valuation)

    def __repr__ (self):
        return 'num_players = ' + str (self.num_players) + ',\nvaluation = ' + str (self.valuation)