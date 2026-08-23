#include <stdio.h>
#include <stdlib.h>

#define NUM_STUDENTS 3
#define NUM_COURSES 5

void init_matrix(float x[NUM_STUDENTS][NUM_COURSES]);
void print_matrix(const float x[NUM_STUDENTS][NUM_COURSES]);


int main()
{
    float grades[NUM_STUDENTS][NUM_COURSES] = {{}};
    init_matrix(grades);
    print_matrix(grades);
    return 0;
}

void init_matrix(float grades[NUM_STUDENTS][NUM_COURSES])
{
    int x,y;
    for(x = 0; x < NUM_STUDENTS; x++)
    {
        printf("\n Student: %d", x + 1);
        for(y = 0; y < NUM_COURSES; y++)
        {
            printf("\n Please enter grade: ");
            scanf("%f", &grades[x][y]);
        }
    }
    return;
}

void print_matrix(const float grades[NUM_STUDENTS][NUM_COURSES])
{
    int x,y;
    for(x = 0; x < NUM_STUDENTS; x++)
    {
        printf("\n Student : %d", x + 1);
        for(y = 0; y < NUM_COURSES; y++)
        {
            printf("\n Grade: %.1f", grades[x][y]);
        }
    }
    return;
}