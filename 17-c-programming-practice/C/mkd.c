#include <stdio.h>

int mkd(int a, int b);

int main(void)
{
    int a,b;
    
    printf("This program calculates the maximum common divisor between 2 numbers!\n");
    printf("Please enter the 1st number:\n ");
    scanf("%d",&a);
    printf("Please enter the 2nd number:\n ");
    scanf("%d",&b);
    printf("The maximum common divisor between %d and %d is %d",a,b,mkd(a,b));
    
    return 0;
}

int mkd(int a, int b)
{
    if (a == b) return a;
    else if (a < b) return mkd(a, b-a);
    else return mkd(a-b, b);
}
