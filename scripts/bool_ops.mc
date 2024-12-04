int main() {
    bool a = true;
    bool b = false;

    if (a && b) {
      return 1; 
    } else if (a || b) {
      printf("a || b\n");
      return -1;
    }

    int c = 5;
    return 0;
}

bool equalator() {
  int a = 5;
    int b = 10;
    if (a == 5 || (b / a) > 2) {
        return false;
    }
    return true;
}