from typing import TypeAlias
import sys

Matrix: TypeAlias = list[list[int]]


def totalCost(mask: int, curr: int, n: int, cost: Matrix, dp: Matrix) -> int:
    if dp[curr][mask] != -1:
        return dp[curr][mask]

    # base case: si toutes les villes sont visitées il faut retourner à la ville de départ
    # on retourne le coût pour aller à la ville de départ
    if mask == (1 << n) - 1:
        return cost[curr][0]

    cout = sys.maxsize

    for i in range(n):
        if (mask & (1 << i)) == 0:
            # si la ville n'est pas visitée
            # on visite la ville en mettant le mask à jour
            cout = min(cout, cost[curr][i] + totalCost(mask | 1 << i, i, n, cost, dp))

    dp[curr][mask] = cout
    return cout


def tsp(cost: Matrix) -> int:
    n = len(cost)
    dp = [[-1] * (1 << n) for _ in range(n)]
    return totalCost(1, 0, n, cost, dp)


if __name__ == "__main__":
    cost = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]

    result = tsp(cost)
    print(result)
