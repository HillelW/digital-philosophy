"""
   implements functions relating to fair allocation of a disputed estate,
   also known as a "bankruptcy problem". 
   
   see Aumann and Maschler's 1985 paper: 
   "Game Theoretic Analysis of a Bankruptcy Problem from the Talmud."
"""


import itertools
from typing import Callable


class AllocationProblem(object):
    def __init__(self, estate: float, claims: list[float]):
        self.claims = claims
        self.estate = estate
        self.is_valid_allocation_problem()

    ######################
    # VALIDATION METHODS #
    ######################

    def is_valid_allocation_problem(self) -> None:
        if not self.is_monotonically_increasing():
            raise ValueError(
                "not a valid allocation problem because the claims are not monotonically increasing!"
            )
        if not self.all_claims_are_greater_than_zero():
            raise ValueError(
                "not a valid allocation problem because the claims are not all greater than zero!"
            )
        if not self.sum_of_claims_exceeds_estate():
            raise ValueError(
                "not a valid allocation problem because the sum of the claims does not exceed the value of the estate!"
            )

    def is_monotonically_increasing(self) -> bool:
        return all(x <= y for x, y in zip(self.claims, self.claims[1:]))

    def all_claims_are_greater_than_zero(self) -> bool:
        return len([claim for claim in self.claims if claim < 0]) == 0

    def sum_of_claims_exceeds_estate(self) -> bool:
        sum_of_claims = sum(self.claims)
        return sum_of_claims > self.estate

    ######################
    # ALLOCATION METHODS #
    ######################

    def proportional_division(self) -> list[float]:
        """
        Example Usage:

        allocation_problem = AllocationProblem (700, [100, 200, 300, 400])
        allocation_problem.proportional_division () == [70, 140, 210, 280]
        """
        sum_of_claims = sum(self.claims)
        return [((claim / sum_of_claims) * self.estate) for claim in self.claims]

    def equal_division_of_gains(self) -> list[float]:
        """
        divides the gains equally, even if one claimant receives more than her initial claim.

        Example Usage:

        allocation_problem = AllocationProblem (700, [100, 200, 300, 400])
        allocation_problem.equal_division_of_gains () == [175.0, 175.0, 175.0, 175.0]

        note: Equal Division of Gains is not sensible if c1 < g/n,
        since (at least) the first creditor who claims the least amount
        will be paid more than she is owed.
        """
        return [(self.estate / len(self.claims)) for claim in self.claims]

    def constrained_equal_division_of_gains(
        self, claims=None, estate=None
    ) -> list[float]:
        """
        divides the gains equally, subject to the restriction that no creditor receives
        more than her claim.

        Mathematically, we choose one number a such that:

        min (c1, a) + . . . + min (cn, a) = estate.

        We grant the amount min (ci, a) to claimant i.

        Example Usage:

        allocation_problem = AllocationProblem (700, [100, 200, 300, 400])
        allocation_problem.proportional_division () == [100, 200, 200, 200]
        """
        if not claims and not estate:
            claims = self.claims
            estate = self.estate
        result = []
        n = len(claims)
        # start by assuming an equal division
        result = [estate / n for claim in claims]
        difference = 0

        for index, claim in enumerate(claims):
            # if a difference must be distributed, do that first
            if difference > 0:
                claimant_indexes = list(range(index, n))
                distributed_difference = difference / len(claimant_indexes)
                for i in claimant_indexes:
                    result[i] += distributed_difference
                difference = 0

            # if current claimant received more than she claims,
            # knock the allocation back down to her claim
            if result[index] > claims[index]:
                difference = result[index] - claims[index]
                result[index] = claims[index]
        return result

    def equal_division_of_losses(self) -> list[float]:
        """
        divides the gains equally, even if one claimant goes into debt as a result of her claim.

        Note: Equal Division of Losses is not sensible if c1 < (s - g)/n,
        where s is the sum of claims, g is the value of the estate, and n is the number of claims,
        since Creditor 1's portion of the estate would be negative in that case.

        Example Usage:

        allocation_problem = AllocationProblem (700, [100, 200, 300, 400])
        allocation_problem.equal_division_of_losses () == [25.0, 125.0, 225.0, 325.0]
        """
        claims = self.claims
        estate = self.estate
        sum_of_claims = sum(self.claims)
        total_loss = sum_of_claims - self.estate
        n = len(self.claims)
        return [claim - (sum_of_claims - estate) / n for claim in claims]

    def constrained_equal_division_of_losses(
        self, claims=None, estate=None
    ) -> list[float]:
        """
        divides the gains equally, subject to the restriction that no claimant
        goes into debt as a result of the division.

        Mathematically, we choose one number a such that:

        max (0, c1 - a) + . . . + max (0, cn - a) = estate.

        We grant the amount min (ci, a) to claimant i.

        Example Usage:

        allocation_problem = AllocationProblem (700, [100, 200, 300, 400])
        allocation_problem.constrained_equal_division_of_losses () == [25, 125, 225, 325]
        """
        result = []
        if not claims and not estate:
            claims = self.claims
            estate = self.estate
        sum_of_claims = sum(claims)

        dual = self.constrained_equal_division_of_gains(claims, sum_of_claims - estate)

        for claim, other in zip(claims, dual):
            difference = claim - other
            result.append(difference)
        return result

    def constrained_equal_division_of_losses_recursive(self) -> list[float]:
        claims = self.claims
        estate = self.estate
        shortfall = sum(claims) - estate
        distributed_loss = shortfall / len(claims)
        result = [claim - distributed_loss for claim in claims]

        negatives = [allocation for allocation in result if allocation < 0]
        if len(negatives) == 0:
            return result

        for index, allocation in enumerate(result):
            if allocation < 0:
                result[index] = 0
        return constrained_equal_division_of_losses()

    def concede_and_divide_with_two(
        self, claims: list[float] = None, estate: float = None
    ) -> list[float]:
        """
        implements the algorithm implicit in Mishnah Bava Metziah 2a as understood
        by Rashi s.v. 'and this one says half is mine.

        Example Usage:

        allocation_problem = AllocationProblem (100, [50, 100])
        allocation_problem.concede_and_divide_with_two () == [25.0, 75.0]
        """
        if not claims and not estate:
            claims = self.claims
            estate = self.estate

        if len(claims) != 2:
            print(
                "can only apply contested garment rule to a case involving exactly two claimants!"
            )
            return None

        concession_of_zero_to_one = max(estate - claims[0], 0)
        concession_of_one_to_zero = max(estate - claims[1], 0)

        contested_portion = (
            estate - concession_of_zero_to_one - concession_of_one_to_zero
        )

        allocation_to_zero = concession_of_one_to_zero + contested_portion / 2
        allocation_to_one = concession_of_zero_to_one + contested_portion / 2
        return [allocation_to_zero, allocation_to_one]

    def concede_and_divide_with_two_dual(
        self, claims: list[float], estate: float
    ) -> list[float]:
        """
        result agrees with concede_and_divide_with_two () since that division rule
        has the property of self-duality.
        """
        if not claims and not estate:
            claims = self.claims
            estate = self.estate

        result = []
        sum_of_claims = sum(claims)

        # temporarily change value of the estate to compute the dual
        self.estate = sum_of_claims - estate
        dual = self.concede_and_divide_with_two()
        # set estate back to its original value
        self.estate = estate
        for claim, other in zip(claims, dual):
            difference = claim - other
            result.append(difference)
        return result

    def concede_and_divide_generalized(
        self, claims: list[float] = None, estate: float = None
    ) -> list[float]:
        """
        generalizes the concede_and_divide_with_two () algorithm to a case with n claimants.

        Example Usage:

        allocation_problem = AllocationProblem (700, [100, 200, 300, 400])
        allocation_problem.concede_and_divide_generalized () == [50, 116.667, 216.667, 316.667]
        """
        if not claims and not estate:
            claims = self.claims
            estate = self.estate

        result = []
        for index, claim in enumerate(claims):
            remaining_claims = claims[(index + 1) :]
            n = len(remaining_claims) + 1
            s = sum(remaining_claims)
            # concede-and-divide is only applied if it returns an order-preserving result
            if (n * claim / 2) <= estate <= (s - (n * claim / 2)):
                new_claims = [claim, s]
                allocation = self.concede_and_divide_with_two(new_claims, estate)
                current_allocation = allocation[0]
                estate -= allocation[0]
                result.append(current_allocation)
            elif estate <= (n * claim / 2):
                allocation = self.constrained_equal_division_of_gains(
                    [claim] + remaining_claims, estate
                )
                return result + allocation
            else:
                allocation = self.constrained_equal_division_of_losses(
                    [claim] + remaining_claims, estate
                )
                return result + allocation
        return result

    def is_bilaterally_consistent(self, claims: list[float], estate: float) -> bool:
        """generalized allocation is consistent with concede-and-divide for two"""
        allocation = self.concede_and_divide_generalized(claims, estate)
        claims_and_allocation = list(zip(claims, allocation))
        pairs = list(itertools.combinations(claims_and_allocation, 2))
        for pair in pairs:
            allocation_sum = pair[0][1] + pair[1][1]
            claims = [pair[0][0], pair[1][0]]
            concede_and_divide_allocation = self.concede_and_divide_with_two(
                claims, allocation_sum
            )

            rounded_concede_and_divide = [
                round(elem, 2) for elem in concede_and_divide_allocation
            ]
            if [
                round(pair[0][1], 2),
                round(pair[1][1], 2),
            ] != rounded_concede_and_divide:
                return False
        return True

    def get_dual_rule(
        self, allocation_rule: Callable[[list[float], float], float]
    ) -> Callable[[list[float], float], float]:
        def dual_rule(claims, estate):
            result = []
            sum_of_claims = sum(claims)
            dual = allocation_rule(claims, sum_of_claims - estate)
            for claim, other in zip(claims, dual):
                difference = claim - other
                result.append(difference)
            return result

        return dual_rule

    ##################################
    # AXIOMATIC VERIFICATION METHODS #
    ##################################

    def is_individually_rational(self, pairs: list[tuple[float, float]]) -> bool:
        """
        each claimant does not end up owing money as the result of an allocation.

        `pairs` has the form [(claim_1, allocation_1), ..., (claim_n, allocation_n)].

         this can be obtained by zipping a claims list with an allocation.
        """
        for pair in pairs:
            if pair[1] < 0:
                return False
        return True

    def is_bounded(self, pairs: list[tuple[float, float]]) -> bool:
        """each claimant cannot get more than the estate"""
        for pair in pairs:
            if pair[1] > pair[0]:
                return False
        return True

    def is_efficient(self, pairs: list[tuple[float, float]], estate: float) -> bool:
        """the entire estate is allocated"""
        result = 0
        for pair in pairs:
            result += pair[1]
        if result == estate:
            return True
        return False

    def is_order_preserving(self, pairs: list[tuple[float, float]]) -> bool:
        differences = [claim - allocation for claim, allocation in pairs]
        diffs = differences[::-1]
        return all(x <= y for x, y in zip(diffs, diffs[1:]))

    def each_claim_is_upper_bounded_by_estate(self) -> bool:
        return len([claim for claim in self.claims if claim > self.estate]) == 0
