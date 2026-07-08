"""
  Part A: I/O-bound work  -> ThreadPoolExecutor (fetching URLs over the network)
  Part B: CPU-bound work  -> ProcessPoolExecutor (computing primes)

Run with:
    python prereqs/concurrency_benchmark.py
"""

from __future__ import annotations #for using modern type hints like list[str] and dict[str, int]

import time #gives access to time.perf_counter() for high-resolution timing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor #executer engines for concurrent execution of tasks

import requests #gives access to the requests library for making HTTP requests(fetching URLs over the network)


# ---------------------------------------------------------------------------
# Part A — I/O-bound benchmark (ThreadPoolExecutor)
# ---------------------------------------------------------------------------

URLS = [
        'https://www.thesportsdb.com/api/v1/json/3/all_leagues.php',
        'https://www.thesportsdb.com/api/v1/json/3/all_countries.php',
        'https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p=Danny_Welbeck',
        'https://www.thesportsdb.com/api/v1/json/3/searchevents.php?e=Arsenal_vs_Chelsea&s=2016-2017',
        'https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php?s=Soccer&c=Switzerland'
]
# JSONPlaceholder is a free fake REST API used for testing
#Each endpoint returns an array of JSON objects, which we can measure the size of in bytes after fetching.


#processing each URL sequentially, one at a time, and returning the size of the response in bytes
def fetch_sequential(urls: list[str]) -> list[int]: #fn takes a list of URLs and returns a list of integers
    sizes = [] #initializing an empty list to store the sizes of the responses in bytes
    for url in urls: #loop over rach URL at a time
        response = requests.get(url) #fetch the URL using the requests library, which sends an HTTP GET request to the specified URL and returns a response object
        sizes.append(len(response.content)) #append the size of the response in bytes to the sizes list
    return sizes
#fetching each URL sequentially makes the program wait for each request to complete before moving on to the next one, so the total wait time is equal to the sum of the time taken for each request.

#processing each URL concurrently using a thread pool, and returning the size of the response in bytes
def fetch_parallel(urls: list[str]) -> list[int]:
   
    with ThreadPoolExecutor(max_workers=len(urls)) as executor: #number of workers is set to the number of URLs, so that each URL can be fetched in parallel by a separate thread.Then, making sure the program shuts down cleanly when done even if an error occurs.
        results = list(executor.map(lambda url: len(requests.get(url).content), urls)) #return a list of sizes of the URLs in bytes, using the lambda function accompanied with the lazy iterator 'map()' to fetch the URLs and get the size of the content without a defined function.
    return results
#fetching URLs concurrently allows threads to overlap and send multiple requests at the same time, so the total wait time is equal to the time taken for the slowest request, which can be much faster than fetching them sequentially.


# ---------------------------------------------------------------------------
# Part B — CPU-bound benchmark (ProcessPoolExecutor)
# ---------------------------------------------------------------------------

def compute_heavy(n: int) -> int:
    """Sum of all primes below n, using a simple sieve of Eratosthenes."""
    if n < 2: #number of elements in the sieve is less than 2 (0 or 1), then there are no primes to sum, so return 0
        return 0
    sieve = bytearray([1]) * n #creating a bytearray of size n, initialized to 1 assuming all numbers are prime. Each index in the array has a value, either 1 for prime or 0 for non-prime.
    #bytearrays are more memory-effecient than lists for larger values of n.
    sieve[0] = sieve[1] = 0 #marking 0 and 1 as non-prime   
    for i in range(2, int(n ** 0.5) + 1): #loop starting from 2 up to the squatre root of n (inclusive). Any non-prime number less than n must have at least one factor less than or equal to the square root of n, so we only need to check for primes up to that point.
        if sieve[i]:#non-null and not zero, meaning i is prime, so we can mark all multiples of i as non-prime.
            for multiple in range(i * i, n, i): #marking the multiples of i as non-prime, starting from i*i (the first multiple of i that is greater than i) up to n, with a step size of i. This ensures that we only mark the multiples of i that are greater than or equal to i*i, since any smaller multiples would have already been marked by smaller prime factors.
                sieve[multiple] = 0
    return sum(i for i, is_prime in enumerate(sieve) if is_prime)


def run_sequential(inputs: list[int]) -> list[int]:
    """Run compute_heavy on each input one at a time."""
    return [compute_heavy(n) for n in inputs]


def run_parallel(inputs: list[int]) -> list[int]:
    """Run compute_heavy on each input concurrently using a process pool."""
    with ProcessPoolExecutor(max_workers=len(inputs)) as executor:
        results = list(executor.map(compute_heavy, inputs))
    return results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_comparison_table(seq_time: float, par_time: float, par_label: str) -> None:
    speedup = seq_time / par_time if par_time > 0 else float("inf") #avoiding division by zero error.
    print(f"{'Method':<14}| {'Time (s)':<10}| Speedup")
    print(f"{'-' * 14}|{'-' * 11}|{'-' * 9}")
    print(f"{'Sequential':<14}| {seq_time:<10.2f}| 1.0x")
    print(f"{par_label:<14}| {par_time:<10.2f}| {speedup:.1f}x")


def benchmark_io() -> None:
    print("=" * 50)
    print("PART A — I/O-bound benchmark (ThreadPoolExecutor)")
    print("=" * 50)

    start = time.perf_counter()
    seq_sizes = fetch_sequential(URLS)
    seq_time = time.perf_counter() - start

    start = time.perf_counter()
    par_sizes = fetch_parallel(URLS)
    par_time = time.perf_counter() - start

    print(f"Sequential response sizes: {seq_sizes}")
    print(f"Parallel response sizes:   {par_sizes}")
    print()
    print_comparison_table(seq_time, par_time, f"ThreadPool({len(URLS)})")
    print()


def benchmark_cpu() -> None:
    print("=" * 50)
    print("PART B — CPU-bound benchmark (ProcessPoolExecutor)")
    print("=" * 50)

    inputs = [500_000, 600_000, 700_000, 800_000]

    start = time.perf_counter()
    run_sequential(inputs)
    seq_time = time.perf_counter() - start

    start = time.perf_counter()
    run_parallel(inputs)
    par_time = time.perf_counter() - start

    print()
    print_comparison_table(seq_time, par_time, f"ProcessPool({len(inputs)})")
    print()


if __name__ == "__main__": #making sure benchmarks only run when execcuted directly, not when imported as a module.
    benchmark_io()
    benchmark_cpu()


# ---------------------------------------------------------------------------
# Why ThreadPoolExecutor helps in Part A but ProcessPoolExecutor is needed
# in Part B:

#In part A, threads spend so much time waiting for I/O over the network, so python releases the GIL allowing other threads to do their work leading to a speedup.
#so threading mainly helps when the workload is I/O-bound, waiting for external responses.

# In Part B, the workload is CPU-bound, so the GIL would have increased the overhead by allowing only one thread to run at a time. Instead, ProcessPoolExecuter allows separate processes to run in parallel each on its own CPU core with its own memory space and GIL, leading to a speedup.
#Regarding this case, the speedup in the sequential version is larger than in the parallel version due to the limited workload so the needed computation in parallel took more time than the sequential version. However, if the workload was larger, the parallel version would have been faster than the sequential version.
#processing mainly helps when the workload is CPU-bound, requiring intensive computation.

# ---------------------------------------------------------------------------