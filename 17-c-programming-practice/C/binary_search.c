#include <stdio.h>

// Function for binary search
int binarySearch(int arr[], int size, int target) {
    int low = 0;
    int high = size - 1;
    
    while(low <= high) {
        int mid = low + (high - low) / 2;  // To avoid overflow for large indices

        if(arr[mid] == target) {
            return mid;
        }
        else if(arr[mid] < target) {
            low = mid + 1;
        }
        else {
            high = mid - 1;
        }
    }
    return -1;  // Target not found
}

int main() {
    int arr[] = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19};
    int size = sizeof(arr) / sizeof(arr[0]);

    int target;
    printf("Enter the number to search: ");
    scanf("%d", &target);

    int result = binarySearch(arr, size, target);

    if(result != -1) {
        printf("Number %d is at index %d\n", target, result);
    }
    else {
        printf("Number %d was not found in the array.\n", target);
    }

    return 0;
}
