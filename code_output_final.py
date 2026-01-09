
def sieve_of_eratosthenes(limit):
    primes = [True] * (limit + 1)
    primes[0] = primes[1] = False
    
    for p in range(2, int(limit**0.5) + 1):
        if primes[p]:
            for i in range(p * p, limit + 1, p):
                primes[i] = False
                
    return [num for num, is_prime in enumerate(primes) if is_prime]

if __name__ == "__main__":
    result = sieve_of_eratosthenes(10000)
    print(result)
