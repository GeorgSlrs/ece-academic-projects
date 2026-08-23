#include <stdio.h>
#include <math.h>


struct point
{
    float x;
    float y;
};

void read_point(struct point * s);
float distance(struct point a, struct point b);

int main(void)
{
    struct point a,b;
    printf("1st point: \n");
    read_point(&a);
    printf("2nd point: \n");
    read_point(&b);
    printf("Distance between the points (%f , %f) and  (%f , %f) is %f", a.x, a.y, b.x, b.y, distance(a,b));
    return 0;
}

void read_point(struct point * s)
{
   printf("Give the x coordinate: \n");
   scanf("%f",&(s->x));
   printf("\nGive the y coordinate: \n");
   scanf("%f",&(s->y));

}

float distance(struct point a, struct point b)
{
    return sqrt((pow(a.x - b.x , 2)) + (pow(a.y - b.y , 2)));
}