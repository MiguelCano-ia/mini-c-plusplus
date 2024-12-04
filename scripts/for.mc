int main() {
    int n = 10; 

    if (n < 0) {
        printf("Error: No se permiten valores negativos para la serie de Fibonacci.\n");
        return 1; // Salida con código de error
    }

    printf("Serie de Fibonacci hasta el término %d:\n", n);

    int a = 0; 
    int b = 1; 
    int c;    

    for(int i = 0; i <= n; i += 1) {
        printf("F(%d) = %d\n", i, a); 

        c = a + b;

        a = b;
        b = c;
    }

    return 0; // Salida exitosa
}
