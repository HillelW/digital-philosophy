class LSystem:
    '''
       implements a Lindenmayer generative grammar (an "L-System").
       conceptually, an L-System differs from a context free grammar in two ways:

       1. it does not have a halting condition.
       2. it can execute multiple string replacements in each iteration.

       based on https://codereview.stackexchange.com/q/129383

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
                         rules = { 'A': 'AB', 'B': 'A' }
                        )

       for i in range (5):
           print (f'depth {i}: ', end='')
           result = system.evaluate (i)
           print ()
    '''
    def __init__ (self, axiom: str, rules: dict):
        self.axiom = axiom
        self.rules = rules

    def evaluate (self, depth: int):
        '''evaluates system by recursively applying the rules on the axiom'''
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