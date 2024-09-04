int main() {
    int a = 10;
    int b = 20;

    if (a < b && b > 15) {
        return 1;
    } else if (a == b || b != 10) {
        return 0;
    }

    return -1;
}