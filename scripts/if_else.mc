int main() {
    int a = 10;
    float b = 20.5;
    bool c = false;

    if (a > b) {
      c = true;
    } else {
      printf("a no es mayor que b\n");
      c = false;
    }

    printf("%f\n", b);

    return 0;
}