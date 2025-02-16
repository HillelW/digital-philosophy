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

def split_estate_equally(estate, num_claimants):
    return estate / num_claimants

def cap_allocation_at_claim(allocation, claim):
    return min(allocation, claim)

def calculate_unmet_claims(capped_allocations, claims):
    return [
        claim - allocation
        for allocation, claim in zip(capped_allocations, claims)
        if allocation < claim
    ]

def no_remaining_unmet_claims(unmet_claims):
    return sum(unmet_claims) == 0

def get_adjusted_allocations(capped_allocations, claims, unmet_claims, remaining_estate):
    adjusted_allocations = capped_allocations[:]
    for i, (allocation, claim) in enumerate(zip(capped_allocations, claims)):
        if allocation < claim:
            proportion = (claim - allocation) / sum(unmet_claims)
            adjusted_allocations[i] += remaining_estate * proportion
    return adjusted_allocations

def redistribute_remaining_estate(remaining_estate, capped_allocation_1, capped_allocation_2, claim_1, claim_2):
    capped_allocations = [capped_allocation_1, capped_allocation_2]
    claims = [claim_1, claim_2]
    unmet_claims = calculate_unmet_claims(capped_allocations, claims)
    
    if no_remaining_unmet_claims(unmet_claims):
        return capped_allocations[0], capped_allocations[1]

    adjusted_allocations = get_adjusted_allocations(capped_allocations, claims, unmet_claims, remaining_estate)
    return adjusted_allocations[0], adjusted_allocations[1]

def equal_division_of_gains(estate, claim_1, claim_2):
    allocation = estate / 2
    return allocation, allocation

def divide_estate_equally(estate, claim_1, claim_2):
    allocation_1, allocation_2 = equal_division_of_gains(estate, claim_1, claim_2)
    return allocation_1

def compute_remaining_estate(estate, capped_allocation_1, capped_allocation_2):
    total_capped_allocations = capped_allocation_1 + capped_allocation_2
    remaining_estate = estate - total_capped_allocations
    return remaining_estate

def get_capped_allocations(equal_allocation, claim_1, claim_2):
    capped_allocation_1 = min(equal_allocation, claim_1)
    capped_allocation_2 = min(equal_allocation, claim_2)
    return capped_allocation_1, capped_allocation_2

def constrained_equal_awards(estate, claim_1, claim_2):
    equal_allocation_of_estate = divide_estate_equally(estate, claim_1, claim_2)
    capped_allocation_1, capped_allocation_2 = get_capped_allocations(equal_allocation_of_estate, claim_1, claim_2)
    remaining_estate = compute_remaining_estate(estate, capped_allocation_1, capped_allocation_2)
    allocation_1, allocation_2 = redistribute_remaining_estate(remaining_estate, capped_allocation_1, capped_allocation_2, claim_1, claim_2)
    return allocation_1, allocation_2

def initialize_half_claims(claims):
    """Compute the half-claims for each creditor."""
    return [claim / 2 for claim in claims]

def distribute_initial_payments(estate, half_claims):
    """
    Distribute the estate equally among all creditors until each receives half their claim.
    If a creditor reaches their half-claim limit, they stop receiving further payments.
    """
    remaining_estate = estate
    allocations = [0] * len(half_claims)

    while remaining_estate > 0:
        active_creditors = [
            i for i, allocation in enumerate(allocations)
            if allocation < half_claims[i]
        ]

        # Exit if no creditors are eligible for further payment
        if not active_creditors:
            break

        # Divide the remaining estate equally among active creditors
        allocation_per_creditor = remaining_estate / len(active_creditors)
        for i in active_creditors:
            potential_payment = allocations[i] + allocation_per_creditor

            # Ensure no creditor exceeds half their claim
            if potential_payment > half_claims[i]:
                remaining_estate -= (half_claims[i] - allocations[i])
                allocations[i] = half_claims[i]
            else:
                remaining_estate -= allocation_per_creditor
                allocations[i] += allocation_per_creditor

    return allocations

def finalize_allocations(estate, claims, allocations):
    """
    Distribute any remaining estate equally among all creditors, ensuring consistency
    after half-claims have been met.
    """
    remaining_estate = estate - sum(allocations)
    num_creditors = len(claims)

    while remaining_estate > 0:
        allocation_per_creditor = remaining_estate / num_creditors

        for i in range(len(allocations)):
            max_possible_payment = claims[i] - allocations[i]
            payment = min(allocation_per_creditor, max_possible_payment)

            allocations[i] += payment
            remaining_estate -= payment

            if remaining_estate <= 0:
                break

    return allocations

def allocate_estate_among_creditors(estate, claims):
    """
    Allocate an estate among creditors using the contested garment consistent algorithm.
    Each creditor can receive at most half their claim, distributed step-by-step.
    """
    # 1. Compute half-claims for all creditors
    half_claims = initialize_half_claims(claims)

    # 2. Distribute initial payments to meet half-claims where possible
    initial_allocations = distribute_initial_payments(estate, half_claims)

    # 3. Finalize allocations to ensure all remaining estate is distributed
    final_allocations = finalize_allocations(estate, claims, initial_allocations)

    return final_allocations


# Example usage:
estate = 100
claims = [100, 200, 300]
allocations = allocate_estate_among_creditors(estate, claims)

print("Estate:", estate)
print("Claims:", claims)
print("Allocations:", allocations)

estate = 200
claims = [100, 200, 300]
allocations = allocate_estate_among_creditors(estate, claims)

print("Estate:", estate)
print("Claims:", claims)
print("Allocations:", allocations)

estate = 300
claims = [100, 200, 300]
allocations = allocate_estate_among_creditors(estate, claims)

print("Estate:", estate)
print("Claims:", claims)
print("Allocations:", allocations)


print(constrained_equal_awards(100, 100, 100))
print(constrained_equal_awards(100, 100, 50))
print(constrained_equal_awards(50, 100, 50))
print(constrained_equal_awards(50, 5, 50))



 


def initialize_allocations(num_claimants):
    """Initialize the allocations as zeros for all claimants."""
    return [0] * num_claimants

def distribute_equally_among_claimants(remaining_estate, remaining_claims):
    """
    Calculate the equal award for claimants who still have outstanding claims.
    """
    active_claimants = sum(1 for claim in remaining_claims if claim > 0)
    if active_claimants == 0:
        return 0  # No claimants left
    return remaining_estate / active_claimants

def cap_allocation_and_update_state(allocations, remaining_claims, remaining_estate, equal_award):
    """
    Cap each claimant's allocation at their remaining claim and update the state.
    """
    for i, remaining_claim in enumerate(remaining_claims):
        if remaining_claim > 0:
            # Allocate the minimum between the equal award and the remaining claim
            allocation = min(equal_award, remaining_claim)
            allocations[i] += allocation
            remaining_claims[i] -= allocation
            remaining_estate -= allocation
    return remaining_estate

def estate_fully_distributed(remaining_estate):
    """Check if the estate has been fully distributed."""
    return remaining_estate <= 0

def constrained_equal_awards(estate, claims):
    """
    Compute the Constrained Equal Awards (CEA) solution for a bankruptcy problem.

    Parameters:
    - estate: Total value of the estate to be distributed.
    - claims: List of claims from creditors.

    Returns:
    - List of allocations to each creditor.
    """
    remaining_estate = estate  # Estate left to distribute
    remaining_claims = claims[:]  # Copy of claims to track remaining amounts
    allocations = initialize_allocations(len(claims))  # Start with zero allocations

    while not estate_fully_distributed(remaining_estate):
        # Step 1: Calculate equal award for active claimants
        equal_award = distribute_equally_among_claimants(remaining_estate, remaining_claims)

        # Step 2: Allocate and update state
        remaining_estate = cap_allocation_and_update_state(
            allocations, remaining_claims, remaining_estate, equal_award
        )

    return allocations


# Example Usage
def run_examples():
    print("Example 1: Estate = 300, Claims = [100, 200, 300]")
    print(constrained_equal_awards(300, [100, 200, 300]))  # Expected: [100, 100, 100]

    print("\nExample 2: Estate = 400, Claims = [100, 200, 300]")
    print(constrained_equal_awards(400, [100, 200, 300]))  # Expected: [100, 150, 150]

    print("\nExample 3: Estate = 500, Claims = [100, 200, 300]")
    print(constrained_equal_awards(500, [100, 200, 300]))  # Expected: [100, 200, 200]

    print("\nExample 4: Estate = 150, Claims = [50, 50, 50]")
    print(constrained_equal_awards(150, [50, 50, 50]))  # Expected: [50, 50, 50]

    print("\nExample 5: Estate = 75, Claims = [50, 50, 50]")
    print(constrained_equal_awards(75, [50, 50, 50]))  # Expected: [25, 25, 25]

run_examples()


def initialize_allocations(num_claimants):
    """Initialize all allocations to 0."""
    return [0] * num_claimants

def calculate_initial_loss(claims, estate):
    """Calculate the initial equal loss for all claimants."""
    total_claims = sum(claims)
    total_loss = total_claims - estate
    return total_loss / len(claims) if total_loss > 0 else 0

def cap_losses_and_update(allocations, remaining_claims, initial_equal_loss):
    """
    Adjust losses to respect constraints, ensuring no loss exceeds a claimant's claim.
    Returns updated loss and remaining claims.
    """
    adjusted_loss = 0  # Loss redistributed in this step
    for i, remaining_claim in enumerate(remaining_claims):
        if remaining_claim > 0:  # Claimant still has an outstanding claim
            # Determine the actual loss for this claimant
            potential_loss = min(initial_equal_loss, remaining_claim)
            allocations[i] += remaining_claim - potential_loss  # Allocate adjusted amount
            adjusted_loss += initial_equal_loss - potential_loss
            remaining_claims[i] = remaining_claim - (remaining_claim - potential_loss)
    return adjusted_loss, remaining_claims

def all_claimants_satisfied(remaining_claims):
    """Check if all claims are satisfied or no further losses can be distributed."""
    return all(claim <= 0 for claim in remaining_claims)

def constrained_equal_losses(estate, claims):
    """
    Compute the Constrained Equal Losses (CEL) solution for a bankruptcy problem.

    Parameters:
    - estate: Total value of the estate to be distributed.
    - claims: List of claims from creditors.

    Returns:
    - List of allocations to each creditor.
    """
    remaining_claims = claims[:]
    allocations = initialize_allocations(len(claims))  # Start with no allocations
    remaining_loss = sum(claims) - estate  # Total loss to distribute

    while remaining_loss > 0 and not all_claimants_satisfied(remaining_claims):
        # Step 1: Compute initial equal loss
        initial_equal_loss = calculate_initial_loss(remaining_claims, estate)

        # Step 2: Cap losses and redistribute remaining loss
        redistributed_loss, remaining_claims = cap_losses_and_update(
            allocations, remaining_claims, initial_equal_loss
        )
        remaining_loss -= redistributed_loss  # Update remaining loss

    # Final step: Assign allocations as claim minus the loss
    return [claim - remaining for claim, remaining in zip(claims, remaining_claims)]


# Example Usage
def run_examples():
    print("Example 1: Estate = 300, Claims = [100, 200, 300]")
    print(constrained_equal_losses(300, [100, 200, 300]))  # Expected: [50, 150, 100]

    print("\nExample 2: Estate = 400, Claims = [100, 200, 300]")
    print(constrained_equal_losses(400, [100, 200, 300]))  # Expected: [66.67, 166.67, 166.67]

    print("\nExample 3: Estate = 150, Claims = [50, 50, 50]")
    print(constrained_equal_losses(150, [50, 50, 50]))  # Expected: [50, 50, 50]

    print("\nExample 4: Estate = 75, Claims = [50, 50, 50]")
    print(constrained_equal_losses(75, [50, 50, 50]))  # Expected: [25, 25, 25]

    print("\nExample 5: Estate = 100, Claims = [30, 40, 50]")
    print(constrained_equal_losses(100, [30, 40, 50]))  # Expected: [30, 35, 35]

run_examples()
