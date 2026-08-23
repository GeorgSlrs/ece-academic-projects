#include <stdio.h>

int main(void) {
    int x[10], y[15], z[20];
    int* ptr[] = {x, y, z};

    // 1. Directly using the array name.
    printf("the address of the first element of x is : %p\n", x);

    // 2. Using array indexing without dereferencing.
    printf("the address of the first element of x is : %p\n", &x[0]);

    // 3. Using pointer arithmetic without dereferencing.
    printf("the address of the first element of x is : %p\n", x + 0);

    // 4. Using the array of pointers `ptr`.
    printf("the address of the first element of x is : %p\n", ptr[0]);

    // 5. Using pointer dereferencing with `ptr`.
    printf("the address of the first element of x is : %p\n", *ptr);

    // 6. Using array of pointers `ptr` with additional indexing.
    printf("the address of the first element of x is : %p\n", &(ptr[0][0]));

    return 0;
}

