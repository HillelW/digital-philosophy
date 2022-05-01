import string


class LSystem:
    '''
       implements a Lindenmayer D0L generative grammar (an "L-System").
       conceptually, a D0L L-System differs from a context free grammar in three ways:

       1. it does not have a halting condition.
       2. it can execute multiple string replacements in each iteration.
       3. it does not distinguish between terminals and non-terminals (no filtering mechanism).

       see: 

       1. Collected Works of Baal ha-Rokeach, Volume 1, Sefer ha-Shem, 93, Amudim, Jerusalem, 2004 (Hebrew).
       2. Collected Works of Baal ha-Rokeach, Volume 1, Sefer ha-Shem, 181, Amudim, Jerusalem, 2004 (Hebrew).
       3. Collected Works of Baal ha-Rokeach, Volume 2, Sodey Rofey Smuchim, 3, Amudim, Jerusalem, 2006 (Hebrew).
       4. Chaim, Vital, Etz Chayim, Sha'ar 18, Ch. 1-2.
       5. Hurwitz, Pinchas, Ta'am Eitzo, 18a-b.
       5. Mateyev, Yoel, "Symbolic Computation And Digital Philosophy in Early Ashkenazic Kabbalah."
       6. Mateyev, Yoel, "Between Enlightenment and Romanticism - Computational Kabbalah of Rabbi Pinchas Elijah Hurwitz."

       Example Usage:
   
       from lindenmayer import LSystem
       
       system = LSystem (
                         axiom = 'A',
                         rules = {'A': 'AB', 'B': 'A'}
                        )

       for i in range (5):
           print (f'depth {i}: ', end='')
           result = system.evaluate (i) # "ABAABABA"
           print ()
    '''
    # TODO: define recognizer. complement of a langauge is A* - L.
    # to compute complement, generate all strings of length n from A*
    # and then subtract all strings of length n from L in each step.
    def __init__ (self, axiom: str, rules: dict):
        self.axiom = axiom
        self.rules = rules

    def evaluate (self, iterations: int):
        result = self.axiom
        for i in range (iterations):
            new = ''
            for char in result:
                if char in self.rules:
                    new += self.rules[char]
                else:
                    new += char
            result = new
            print (result)
        return result

    def evaluate_recursive (self, depth: int):
        '''
           evaluates system by recursively applying the rules on the axiom.
           based on https://codereview.stackexchange.com/q/129383
        '''
        for symbol in self.axiom:
            self.evaluate_symbol (symbol, depth)
        return None

    def evaluate_symbol (self, symbol: str, depth: int):
        '''recursively applies the production rules to one symbol'''
        if depth <= 0 or symbol not in self.rules:
            print (symbol, end='')
        else:
            for produced_symbol in self.rules[symbol]:
                self.evaluate_symbol (produced_symbol, depth - 1)
        return None

    def enumerate_strings (self):
        pass

    def enumerate_complement (self):
        pass

    def get_alphabet (self):
        alphabet = set ()
        values = list(set(self.rules.values()))
        for value in values:
            for symbol in value:
                alphabet.add (symbol)
        alphabet = list (alphabet)
        return alphabet

    def get_complement_alphabet (self):
        alphabet = self.get_alphabet ()
        result_alphabet = [x.upper() for x in string.ascii_lowercase]
        for char in alphabet:
            result_alphabet.remove (char)
        return result_alphabet

    def is_in_language (self, string):
        i = 1
        while True:
            current = enumerate_lexicographically (max_lenth=i)
            complement = enumerate_lexicographically (alphabet=None)
            pass

    def enumerate_lexicographically (self, max_length=3, alphabet=None):
        '''given an alphabet A, enumerates words from A* in lexicographic order.'''
        print (alphabet)
        reversed_alphabet = list(reversed(alphabet))
        nodes_to_visit = ['']

        while nodes_to_visit:
            current_node = nodes_to_visit.pop ()
            
            if len(current_node) > max_length:
                continue

            yield current_node
            nodes_to_visit.extend (current_node + tc for tc in reversed_alphabet)