#include <stdio.h>
#include <math.h>

double f(double x);

int main(void)
{
    double d;

    printf("Enter a number: \n");
    scanf("%lf", &d);
    return 0;

    printf("Result: %lf", f(d));
}

double f(double x)
{
    return 1 / (1 + exp(-x));
}