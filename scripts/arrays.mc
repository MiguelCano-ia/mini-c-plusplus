int main() {
    int arr[5];
    arr[0] = 10;
    arr[1] = arr[0] + 20;
    int x = arr[1];

    printf("arr[0]: %d\n", arr[0]);
    printf("arr[1]: %d\n", arr[1]);
    printf("x: %d\n", x);
    return 0;
}
