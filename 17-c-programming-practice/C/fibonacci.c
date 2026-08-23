#include <stdio.h>
#include <stdlib.h>


#define MAX 1000

long long memo[MAX];


long long fibonacci(int n);


int main() {
  // Initialize the memo array with -1, to signify uncalculated values
  for (int i = 0; i < MAX; i++) {
    memo[i] = -1;
  }

  int n;
  printf("Enter a number: ");
  scanf("%d", &n);

  printf("Fibonacci of %d: %lld\n", n, fibonacci(n));

  return 0;
}

long long fibonacci(int n) {
  // Base cases
  if (n == 0) return 0;
  if (n == 1) return 1;

  // Check if the result is already in the memo array
  if (memo[n] != -1) return memo[n];

  // Otherwise, calculate and store the result in the memo array
  memo[n] = fibonacci(n - 1) + fibonacci(n - 2);
  return memo[n];
}
