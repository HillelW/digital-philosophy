'''
   implements functions relating to fair allocation of a disputed good,
   also known as a "bankruptcy problem". 
   
   see Aumann and Maschler's 1985 paper: 
   "Game Theoretic Analysis of a Bankruptcy Problem from the Talmud."
'''


import itertools
from typing import Callable
from typing import List
from typing import Tuple


class Allocation (object):
    '''represents an allocation problem'''
    def __init__ (self, claims: List[float], good: float):
        '''
           given a list of claims and a good which is to be allocated
           amongst the claimants, creates an object representing the
           corresponding allocation problem.

           Example Usage:

           allocation = Allocation ([1, 1], 1)
           allocation.proportional_division ()
        '''
        # verify that we are dealing with a valid allocation problem
        if not self.is_valid_allocation_problem ():
            if not self.is_monotonically_increasing ():
                raise ValueError ('not a valid allocation problem because the claims are not monotonically increasing!')
            elif not self.all_claims_are_greater_than_zero ():
                raise ValueError ('not a valid allocation problem because the claims are not all greater than zero!')
            elif not self.sum_of_claims_exceeds_good ():
                raise ValueError ('not a valid allocation problem because the sum of the claims does not exceed the value of the good!')

        self.claims = claims
        self.good = good

    ##############################
    # HELPER VALIDATION METHODS  #
    ##############################

    def is_valid_allocation_problem (self) -> bool:
        '''returns True if it's a valid allocation problem, False otherwise.'''
        return self.is_monotonically_increasing () and self.all_claims_are_greater_than_zero () and self.sum_of_claims_exceeds_good () and self.each_claim_is_upper_bounded_by_good ()

    def is_monotonically_increasing (self) -> bool:
        '''returns True if the claims are monotonically increasing, False otherwise.'''
        return all (x <= y for x, y in zip (self.claims, self.claims[1:]) )

    def all_claims_are_greater_than_zero (self) -> bool:
        '''returns True if the claims are all greater than zero, False otherwise.'''
        return len ([claim for claim in self.claims if claim < 0]) == 0

    def sum_of_claims_exceeds_good (self) -> bool:
        '''returns True if the sum of the claims exceeds the value of the good, False otherwise.'''
        sum_of_claims = sum (self.claims)
        return sum_of_claims > self.good

    ######################
    # ALLOCATION METHODS #
    ######################

    def proportional_division (self) -> List[float]:
        '''
           Example Usage: 

           allocation = Allocation ([100, 200, 300, 400], 700)
           allocation.proportional_division () == [70, 140, 210, 280]
        '''
        sum_of_claims = sum (self.claims)
        return [ ((claim / sum_of_claims) * self.good) for claim in self.claims ]

    def equal_division_of_gains (self) -> List[float]:
        '''
           divides the gains equally, even if one claimant receives more than her initial claim.

           Example Usage:

           allocation = Allocation ([100, 200, 300, 400], 700)
           allocation.equal_division_of_gains () == [175.0, 175.0, 175.0, 175.0]

           note: Equal Division of Gains is not sensible if c1 < g/n, 
           since (at least) the first creditor who claims the least amount 
           will be paid more than she is owed.
        '''
        return [ (self.good / len (self.claims)) for claim in self.claims ]

    def constrained_equal_division_of_gains (self, claims=None, good=None) -> List[float]:
        '''
           divides the gains equally, subject to the restriction that no creditor receives 
           more than her claim.

           Mathematically, we choose one number a such that:

           min (c1, a) + . . . + min (cn, a) = good.

           We grant the amount min (ci, a) to claimant i.

           Example Usage: 

           allocation = Allocation ([100, 200, 300, 400], 700)
           allocation.proportional_division () == [100, 200, 200, 200]
        '''
        if not claims and not good:
            claims = self.claims
            good = self.good
        result = []
        n = len (claims)
        # start by assuming an equal division
        result = [good / n for claim in claims]
        difference = 0

        for index, claim in enumerate (claims):
            # if a difference must be distributed, do that first
            if difference > 0:
                claimant_indexes = list (range (index, n))
                distributed_difference = difference / len (claimant_indexes)
                for i in claimant_indexes:
                    result[i] += distributed_difference
                difference = 0

            # if current claimant received more than she claims,
            # knock the allocation back down to her claim
            if result[index] > claims[index]:
                difference = result[index] - claims[index]
                result[index] = claims[index]
        return result

    def equal_division_of_losses (self) -> List[float]:
        '''
           divides the gains equally, even if one claimant goes into debt as a result of her claim.

           Note: Equal Division of Losses is not sensible if c1 < (s − g)/n, 
           where s is the sum of claims, g is the value of the good, and n is the number of claims,
           since Creditor 1’s portion of the estate would be negative in that case.

           Example Usage: 

           allocation = Allocation ([100, 200, 300, 400], 700)           
           allocation.equal_division_of_losses () == [25.0, 125.0, 225.0, 325.0]
        '''
        claims = self.claims
        good = self.good
        sum_of_claims = sum (self.claims)
        total_loss = sum_of_claims - self.good
        n = len (self.claims)
        return [claim - (sum_of_claims - good) / n for claim in claims]

    def constrained_equal_division_of_losses (self, claims=None, good=None) -> List[float]:
        '''
           divides the gains equally, subject to the restriction that no claimant 
           goes into debt as a result of the division.

           Mathematically, we choose one number a such that:

           max (0, c1 - a) + . . . + max (0, cn - a) = good.

           We grant the amount min (ci, a) to claimant i.

           Example Usage: 

           allocation = Allocation ([100, 200, 300, 400], 700)
           allocation.constrained_equal_division_of_losses () == [25, 125, 225, 325]
        '''
        result = []
        if not claims and not good:
            claims = self.claims
            good = self.good
        sum_of_claims = sum (claims)
        
        # temporarily change value of the good to compute the dual
        # self.good = sum_of_claims - good
        dual = self.constrained_equal_division_of_gains (claims, sum_of_claims - good) 
        # set good back to its original value
        # self.good = good
        for claim, other in zip (claims, dual):
            difference = claim - other
            result.append (difference)
        return result

    def constrained_equal_division_of_losses_recursive (self) -> List[float]:
        claims = self.claims
        good = self.good
        shortfall = sum (claims) - good
        distributed_loss = shortfall / len (claims)
        result = [claim - distributed_loss for claim in claims]

        negatives = [allocation for allocation in result if allocation < 0]
        if len (negatives) == 0:
            return result
        
        for index, allocation in enumerate (result):
            if allocation < 0:
                result[index] = 0
        return constrained_equal_division_of_losses ()

    def concede_and_divide_with_two (self, claims: List[float]=None, good: float=None) -> List[float]:
        '''
           implements the algorithm implicit in Mishnah Bava Metziah 2a as understood 
           by Rashi s.v. 'and this one says half is mine.

           Example Usage:

           allocation = Allocation ([50, 100], 100)
           allocation.concede_and_divide_with_two () == [25.0, 75.0]
        '''
        if not claims and not good:
            claims = self.claims
            good = self.good
        
        if len (claims) != 2:
            print ('can only apply contested garment rule to a case involving exactly two claimants!')
            return None

        concession_of_zero_to_one = max (good - claims[0], 0)
        concession_of_one_to_zero = max (good - claims[1], 0)

        contested_portion = good - concession_of_zero_to_one - concession_of_one_to_zero

        allocation_to_zero = concession_of_one_to_zero + contested_portion / 2 
        allocation_to_one = concession_of_zero_to_one + contested_portion / 2
        return [allocation_to_zero, allocation_to_one] 

    def concede_and_divide_with_two_dual (self, claims: List[float], good: float) -> List[float]:
        '''
           result agrees with concede_and_divide_with_two () since that division rule
           has the property of self-duality.
        '''
        if not claims and not good:
            claims = self.claims
            good = self.good
        
        result = []
        sum_of_claims = sum (claims)

        # temporarily change value of the good to compute the dual
        self.good = sum_of_claims - good
        dual = self.concede_and_divide_with_two () 
        # set good back to its original value
        self.good = good
        for claim, other in zip (claims, dual):
            difference = claim - other
            result.append (difference)
        return result

    def concede_and_divide_generalized (self, claims: List[float]=None, good: float=None) -> List[float]:
        '''      
           generalizes the concede_and_divide_with_two () algorithm to a case with n claimants.     
           
           Example Usage: 

           allocation = Allocation ([100, 200, 300, 400], 700)
           allocation.concede_and_divide_generalized () == [50, 116.667, 216.667, 316.667]
        '''
        if not claims and not good:
            claims = self.claims
            good = self.good

        result = []
        for index, claim in enumerate (claims):
            remaining_claims = claims[(index + 1) :]
            n = len (remaining_claims) + 1
            s = sum (remaining_claims)
            # concede-and-divide is only applied if it returns an order-preserving result
            if (n * claim / 2) <= good <= (s - (n * claim / 2)):
                new_claims = [claim, s]
                allocation = self.concede_and_divide_with_two (new_claims, good)
                current_allocation = allocation[0]
                good -= allocation[0]
                result.append (current_allocation)
            elif  good <= (n * claim / 2):
                allocation = self.constrained_equal_division_of_gains ([claim] + remaining_claims, good)
                return result + allocation
            else:
                allocation = self.constrained_equal_division_of_losses ([claim] + remaining_claims, good)
                return result + allocation
        return result

    def is_bilaterally_consistent (self, claims: List[float], good: float) -> bool:
        '''generalized allocation is consistent with concede-and-divide for two'''
        allocation = self.concede_and_divide_generalized (claims, good)
        print ('\nallocation vector according to generalized rule:')
        print (allocation)
        claims_and_allocation = list (zip(claims, allocation))
        pairs = list (itertools.combinations(claims_and_allocation, 2))
        for pair in pairs:
            allocation_sum = pair[0][1] + pair[1][1]
            claims = [pair[0][0], pair[1][0]]
            concede_and_divide_allocation = self.concede_and_divide_with_two (claims, allocation_sum)
            print (f'\nallocation to {claims} according to generalized rule:')
            print ([pair[0][1], pair[1][1]])
            print (f'\nallocation to {claims} according to concede and divide:')
            print (concede_and_divide_allocation)
            rounded_concede_and_divide = [round (elem, 2) for elem in concede_and_divide_allocation]
            if [round(pair[0][1], 2), round(pair[1][1], 2)] != rounded_concede_and_divide:
                return False
        return True

    def get_dual_rule (self, allocation_rule: Callable[[List[float], float], float]) -> Callable[[List[float], float], float]:
        '''
            given an allocation rule and an allocation problem, 
            returns the corresponding dual allocation rule.
        '''
        def dual_rule (claims, good):
            result = []
            sum_of_claims = sum (claims)
            dual = allocation_rule (claims, sum_of_claims - good) 
            for claim, other in zip (claims, dual):
                difference = claim - other
                result.append (difference)
            return result
        return dual_rule

    ############################
    # HELPER PREDICATE METHODS #
    ############################

    def is_individually_rational (self, pairs: List[Tuple[float, float]]) -> bool:
        '''
           each claimant does not end up owing money as the result of an allocation.

           `pairs` has the form [(claim_1, allocation_1), ..., (claim_n, allocation_n)].

            this can be obtained by zipping a claims list with an allocation.
        '''
        for pair in pairs:
            if pair[1] < 0:
                return False
        return True

    def is_bounded (self, pairs: List[Tuple[float, float]]) -> bool:
        '''each claimant cannot get more than the good'''
        for pair in pairs:
            if pair[1] > pair[0]:
                return False
        return True

    def is_efficient (self, pairs: List[Tuple[float, float]], good: float) -> bool:
        '''the entire good is allocated'''
        result = 0
        for pair in pairs:
            result += pair[1]
        if result == good:
            return True
        return False

    #########################################
    # optional conditions for an allocation #
    #########################################

    def is_order_preserving (self, pairs: List[Tuple[float, float]]) -> bool:
        differences = [claim - allocation for claim, allocation in pairs]
        diffs = differences[::-1]
        return all (x <= y for x, y in zip (diffs, diffs[1:]))

    def each_claim_is_upper_bounded_by_good (self) -> bool:
        return len ([claim for claim in self.claims if claim > self.good]) == 0