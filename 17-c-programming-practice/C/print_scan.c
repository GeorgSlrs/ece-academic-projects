#include <stdio.h>

#define M 5

void print(int N);
void create_vector(void);

int main(void)
{
    int number;
    int number2;
    float number3;

    while (1)
    {
        printf("\nPlease enter an integer number between 1 and 4: \n");
        do
        {
            scanf("%d",&number);
        } while (number > 4 || number < 1);
        
        switch(number)
        {
            case 1:
                printf("\nPlease enter an integer number\n");
                scanf("%d",&number2);
                printf("The square of the given number is %d\n", number2 * number2);
                break;

            case 2:
                printf("\nPlease enter an integer number: \n");
                scanf("%d",&number2);
                print(number2);
                break;

            case 3:
                printf("\nPlease enter a float variable: \n");
                scanf("%f",&number3);
                printf("The number divided by 4, with 4 digits precision is equal to %.4f\n", number3 / 4);
                break;

            case 4:
                create_vector();
                break;

            default:
                break;
        }
    }
    return 0;
}


void print(int N)
{
    for(int i = 0; i < N; i ++)
    {
        printf("Good morning!\n");
    }
}

void create_vector(void)
{
    float vector[M];
    float average = 0.0;

    for(int i = 0; i < M; i ++)
    {
        printf("Please enter the element #%d of the vector: \n", i+1);
        scanf("%f",&vector[i]);
        average += vector[i];
    }

    printf("Average is %.2f\n", average / M);
}
