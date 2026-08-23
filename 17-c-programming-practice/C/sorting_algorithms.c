#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 10000
#define TRUE 1
#define FALSE 0

void init_array(int *array, int n, int a, int b);
void copy_array(int *dest, int *src, int n);
void print_array(int *array, int n);
void swap(int *a, int *b);
int bubble_sort(int *array, int n);
int selection_sort(int *array, int n);
int insertion_sort(int *array, int n);
void mergesort(int *array, int start, int finish, int *cnt);
void merge(int *array, int start, int finish, int *cnt);
void quicksort(int *array, int start, int finish, int *cnt);
int partition(int *array, int start, int finish, int *cnt);
int shell_sort(int *array, int n);
void heapify(int *array, int n, int i, int *cnt);
int heap_sort(int *array, int n);
void max_heapify(int *array, int n, int i, int *cnt);


#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 10000



int main() {
    int array[SIZE];
    int source[SIZE];
    int N = SIZE;
    int cnt; 

    clock_t start_time, end_time;
    double elapsed_time;

    // Initialize a source array with random values
    init_array(source, N, 0, 5000);

    // Bubble Sort
    copy_array(array, source, N);
    start_time = clock();
    cnt = bubble_sort(array, N);
    end_time = clock();
    elapsed_time = ((double) (end_time - start_time)) / CLOCKS_PER_SEC;
    printf("\nBubbleSort Time: %f seconds, Comparisons: %d", elapsed_time, cnt);

    // Selection Sort
    copy_array(array, source, N);
    start_time = clock();
    cnt = selection_sort(array, N);
    end_time = clock();
    elapsed_time = ((double) (end_time - start_time)) / CLOCKS_PER_SEC;
    printf("\nSelectionSort Time: %f seconds, Comparisons: %d", elapsed_time, cnt);

    // Insertion Sort
    copy_array(array, source, N);
    start_time = clock();
    cnt = insertion_sort(array, N);
    end_time = clock();
    elapsed_time = ((double) (end_time - start_time)) / CLOCKS_PER_SEC;
    printf("\nInsertionSort Time: %f seconds, Comparisons: %d", elapsed_time, cnt);

    // Merge Sort
    copy_array(array, source, N);
    start_time = clock();
    cnt = 0;
    mergesort(array, 0, N-1, &cnt);
    end_time = clock();
    elapsed_time = ((double) (end_time - start_time)) / CLOCKS_PER_SEC;
    printf("\nMergeSort Time: %f seconds, Comparisons: %d", elapsed_time, cnt);

    // Quick Sort
    copy_array(array, source, N);
    start_time = clock();
    cnt = 0;
    quicksort(array, 0, N-1, &cnt);
    end_time = clock();
    elapsed_time = ((double) (end_time - start_time)) / CLOCKS_PER_SEC;
    printf("\nQuickSort Time: %f seconds, Comparisons: %d", elapsed_time, cnt);

    // Heap Sort
    copy_array(array, source, N);
    start_time = clock();
    cnt = heap_sort(array, N);
    end_time = clock();
    elapsed_time = ((double) (end_time - start_time)) / CLOCKS_PER_SEC;
    printf("\nHeapSort Time: %f seconds, Comparisons: %d", elapsed_time, cnt);

    // Shell Sort
    copy_array(array, source, N);
    start_time = clock();
    cnt = shell_sort(array, N);
    end_time = clock();
    elapsed_time = ((double) (end_time - start_time)) / CLOCKS_PER_SEC;
    printf("\nShellSort Time: %f seconds, Comparisons: %d", elapsed_time, cnt);

    return 0;
}



void init_array(int *array, int n, int a, int b) {
    srand(time(NULL));
    for (int i = 0; i < n; i++)
        array[i] = a + rand() % (b - a + 1);
}

void copy_array(int *dest, int *src, int n) {
    for (int i = 0; i < n; i++)
        dest[i] = src[i];
}

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int bubble_sort(int *array, int n) {
    int i, j;
    int cnt = 0; 
    int swapped; // This flag is used to check if any swaps happen in an iteration

    for (i = 0; i < n; i++) {
        swapped = 0; // Initialize swapped to false before each pass

        for (j = n - 1; j > i; j--) {
            cnt++;
            if (array[j] < array[j - 1]) {
                swap(&array[j], &array[j - 1]);
                swapped = 1; // If we enter here, a swap was made
            }
        }

        // If no two elements were swapped by the inner loop, then the list is sorted
        if (swapped == 0) {
            break;
        }
    }
    return cnt; 
}


int selection_sort(int *array, int n)
{
	int i,j,pos;
	int cnt=0; 
	
	for (i=0; i<n; i++)
	{
		pos=i;
	
		for (j=i+1; j<n; j++)
		{
			cnt++; 
			if (array[j]<array[pos])
				pos=j;
		}
	
		swap(&array[i], &array[pos]);
	}	
	return cnt; 
}

int insertion_sort(int *array, int n)
{
	int i,j;
	int cnt=0; 
	
	for (i=1; i<n; i++)
	{
		for (j=i; j>=1; j--)
		{
			cnt++; 
			if (array[j]<array[j-1])
				swap(&array[j], &array[j-1]);
			else
				break;
		}
	}	
	
	return cnt; 
}


void mergesort(int *array, int start, int finish, int *cnt)
{
	int i,middle;
	
	if (start==finish) /* 1 element */
		return;
	else if (start==finish-1) /* 2 elements */
	{
		(*cnt)++;
		if (array[start]>array[finish])
			swap(&array[start], &array[finish]);
	}
	else
	{
		middle=(start+finish)/2;
		mergesort(array,start,middle, cnt);
		mergesort(array,middle+1,finish, cnt);
		merge(array,start,finish, cnt);
	}
}

void merge(int *array, int start, int finish, int *cnt)
{
	int C[SIZE];
	int i,j,k;
	int middle, n, m;
	
	middle=(start+finish)/2;
	
	/* 1st array array[start..middle]=array[i..n] */	
	i=start;
	n=middle;
	/* 2nd array array[middle+1..finish]=array[j...m] */	
	j=middle+1;
	m=finish;
	/* new array from merging */	
	k=0;
	
	/* 1.merging of the 2 arrays */
	while (i<=n && j<=m)
	{
		(*cnt)++;
		if (array[i]<array[j])
		{
			C[k]=array[i];
			k++;
			i++;
		}
		else
		{
			C[k]=array[j];
			k++;
			j++;
		}
	}
	
	/* 2. Copy of the reamining array in the end of the new array*/
	
	if (i==n+1) /* 1st array finished */
	{
		while (j<=m)
		{
			C[k]=array[j];
			k++;
			j++;
		}
	}
	else /* 2nd array finished */
	{
		while (i<=n)
		{
			C[k]=array[i];
			k++;
			i++;
		}
	}	
	
	/* 3. Copy of C to the array */
	
	k=0;
	
	i=start;
	while (i<=finish)
	{
		array[i]=C[k];
		i++;
		k++;
	}
}

void quicksort(int *array, int start, int finish, int *cnt)
{
	int i,pos;	
	if (start<finish)
	{				
		pos=partition(array,start,finish, cnt);
		quicksort(array,start,pos-1, cnt);
		quicksort(array,pos+1,finish, cnt);
	}
}

int partition(int *array, int start, int finish, int *cnt)
{
	int pivot, i, j;
	

	pivot=array[start];
	
	i=start+1;
	j=finish;
	
	while(1)
	{
		(*cnt)++;
		while(array[i]<=pivot && i<=finish)
		{
			i++;
			(*cnt)++; 
		}
			

		while(array[j]>pivot && j>=start)
		{
			j--;
			(*cnt)++; 
		}
			

		if (i<j)
			swap(&array[i],&array[j]);
		else
		{
			swap(&array[start],&array[j]);
			return j;
		}
			
	}

}

// Helper functions for heap_sort:
void max_heapify(int *array, int n, int i, int *cnt) {
    int largest = i;
    int left = 2 * i + 1;
    int right = 2 * i + 2;

    if (left < n) {
        (*cnt)++;
        if (array[left] > array[largest])
            largest = left;
    }

    if (right < n) {
        (*cnt)++;
        if (array[right] > array[largest])
            largest = right;
    }

    if (largest != i) {
        swap(&array[i], &array[largest]);
        max_heapify(array, n, largest, cnt);
    }
}

int heap_sort(int *array, int n) {
    int cnt = 0;
    for (int i = n / 2 - 1; i >= 0; i--) {
        max_heapify(array, n, i, &cnt);
    }

    for (int i = n - 1; i > 0; i--) {
        swap(&array[0], &array[i]);
        max_heapify(array, i, 0, &cnt);
    }

    return cnt;
}

int shell_sort(int *array, int n) {
    int cnt = 0;
    for (int gap = n / 2; gap > 0; gap /= 2) {
        for (int i = gap; i < n; i += 1) {
            int temp = array[i];
            int j;
            for (j = i; j >= gap && array[j - gap] > temp; j -= gap) {
                cnt++;
                array[j] = array[j - gap];
            }
            array[j] = temp;
        }
    }
    return cnt;
}
