#include <stdio.h>
#include <math.h>


int is_even(int n);
int is_odd(int n);
int is_square(int n);
int is_cube(int n);

int main(void)
{
    int number;
    printf("Please enther the number to see it's properties\n");
    scanf("%d", &number);

    if (is_even(number)) printf("\nIt's an even number\n");
    if (is_odd(number)) printf("\nIt's an odd number\n");
    if (is_square(number)) printf("\nIt's a square number\n");
    if (is_cube(number)) printf("\nIt's a cube number\n");


    return 0;
}

int is_even(int n)
{
    return (n%2 == 0);
}

int is_odd(int n)
{
    return !(n%2 == 0);
}

int is_square(int n)
{
    return (floor(pow(n, 0.5)) == pow(n,0.5));
}


int is_cube(int n)
{
    return (floor(pow(n, 1/3)) == pow(n,1/3));
}
