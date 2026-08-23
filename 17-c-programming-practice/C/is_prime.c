#include <stdio.h>
#include <math.h>

int is_prime(int n);

int main(void)
{
    int beginning, end;

    printf("Please enter the beginning of the interval\n");
    scanf("%d", &beginning);
    printf("Please enter the end of the interval\n");
    scanf("%d", &end);

    for (int j = beginning; j <= end; j++)
    {
        if(is_prime(j)) printf("The number %d is prime!\n", j);
    }

    return 0;
}

int is_prime(int n)
{
    if (n <= 1) {
        return 0; // 0, 1, and negative numbers are not prime
    }

    for (int i = 2; i <= pow(n, 0.5); i++)
    {
        if (n % i == 0) return 0; // Found a divisor, not prime
    }
    return 1; // No divisors found, number is prime
}
