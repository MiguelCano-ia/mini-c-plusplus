int main() {
  for (int i = 0; i < 5; i = i + 1) {
    printf("%d\n", i);
    if (i == 3) {
        printf("i es igual a 3\n");
        break;
    }
  } 
  return 0;
}