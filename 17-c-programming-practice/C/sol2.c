#include <stdio.h>
#include <math.h>

int rizes(float a, float b, float c, float *x1, float *x2);

int main(void)
{
    float a, b, c, x1, x2;

    printf("This program calculates the solutions of a quadratic equation\n");
    printf("If x1 and x2 have weird values, then It means that there are no solutions to the equation given-not even complex.\n");
    printf("In every other case, the equation has exactly 2 solutions.\n");
    printf("Please enter a: \n");
    scanf("%f", &a);
    printf("Please enter b: \n");
    scanf("%f", &b);
    printf("Please enter c: \n");
    scanf("%f", &c);

    printf("The equation has %d solutions. x1 = %f and x2 = %f\n", rizes(a, b, c, &x1, &x2), x1, x2);

    return 0;
}

int rizes(float a, float b, float c, float *x1, float *x2)
{
    float discriminant = pow(b, 2) - 4 * a * c;

    if (discriminant < 0 || (a == 0 && b == 0 && c != 0))
    {
        return 0;
    }
    else if (a == 0 && b != 0)
    {
        *x1 = *x2 = -c / b;
        return 1;
    }

    *x1 = (-b + sqrt(discriminant)) / (2 * a);
    *x2 = (-b - sqrt(discriminant)) / (2 * a);

    return 2;
}
