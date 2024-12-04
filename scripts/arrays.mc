int main() {
    int arr[10];

    arr[0] = 5;
    arr[1] = 3;
    arr[2] = 8;
    arr[3] = 1;
    arr[4] = 9;
    arr[5] = 2;
    arr[6] = 7;
    arr[7] = 4;
    arr[8] = 6;
    arr[9] = 0;

    printf("Arreglo original:\n");
    for(int i = 0; i < 10; i += 1) {
        printf("arr[%d] = %d\n", i, arr[i]);
    }

    for(int i = 0; i < 10 - 1; i += 1) { 
        for(int j = 0; j < 10 - i - 1; j += 1) { 
            if(arr[j] > arr[j + 1]) {
                // Intercambiar arr[j] y arr[j + 1]
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    printf("\nArreglo ordenado (Bubble Sort):\n");
    for(int i = 0; i < 10; i += 1) {
        printf("arr[%d] = %d\n", i, arr[i]);
    }

    return 0; 
}
