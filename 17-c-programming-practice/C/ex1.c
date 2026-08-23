#include <stdio.h>


float compute_addition(float, float);
float compute_subtraction(float, float);
float compute_multiplication(float, float);
float compute_division(float, float);
void read_values_from_keyboard(float *, float *);

int main(void)
{
 float x,y;
 char operation;

 read_values_from_keyboard(&x,&y);
 printf("\nPlease enter the operation type: + - * / \n");
 scanf("\n%c", &operation);

 switch(operation)
 {
 case '+':
    printf("Addition: %.3f",compute_addition(x,y)); 
    break;
 case '-':
    printf("Subtraction: %.3f",compute_subtraction); 
    break;
 case '*':
    printf("Multiplication: %.3f",compute_multiplication(x,y)); 
    break;
 case '/':
    printf("Division: %.3f",compute_division(x,y)); 
    break;

    default:
        printf("\nPlease enter 1 of the following symbols:  + - * / \n");
 break;
 }

 
 return 0;
}


//If we didn't use pointers then x and y will have 'rubbish' stored in them after the function is executed.
void read_values_from_keyboard(float *x, float *y)
{
    printf("Please enther the value for the 1st number: \n");
    scanf("%f",x);
    printf("Please enther the value for the 2nd number: \n");
    scanf("%f",y);
    printf("\n 1st number: %f and 2nd number: %f",*x,*y);
}



float compute_addition(float x, float y)
{
    return x+y;
}


float compute_subtraction(float x, float y)
{
    return x-y;
}


float compute_multiplication(float x, float y)
{
    return x*y;
}


float compute_division(float x, float y)
{
    return x*y;
}

