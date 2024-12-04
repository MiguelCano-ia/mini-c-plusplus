int main() {
    int a = 10;
    int b = 20;

    if (a < b && b > 15) {
        printf("a < b && b > 15\n");
        return 1;
    } else if (a == b || b != 10) {
      printf("a == b || b != 10\n");
        return 0;
    }

    return -1;
}

int equalor (){
  int a = 5;
    int b = 10;

    if (a >= b) {
        return 1;
    } else if (a <= b) {
        return 0;
    } else {
        return -1;
    }
}