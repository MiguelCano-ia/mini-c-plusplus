string format = "%d %f %s %c";

int main() {
    int intValue = 42;
    float floatValue = 3.14;
    string stringValue = "Hello, world!";

    // Caso 1: Uso correcto de printf con varios especificadores de formato
    printf("%d %f %s", intValue, floatValue, stringValue);
    //   printf("hola"); Caso 5: Uso correcto con variable de formato
 
    return 0;
}
