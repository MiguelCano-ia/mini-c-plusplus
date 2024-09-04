int main() {
    bool a = true;
    bool b = false;

    if (a && b) {
        return 1;
    } else if (a || b) {
        return 0;
    }

    return -1;
}