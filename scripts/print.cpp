// Prueba de printf con diferentes tipos
int main() {
    int edad = 25;
    float promedio = 89.5;
    string nombre = "Alice";

    // Correcto: número de especificadores coincide con los argumentos
    printf("Edad: %d, Promedio: %f, Nombre: %s\n", edad, promedio, nombre);
    // Correcto: especificador de cadena con string
    printf("Hola, %s\n", nombre);

    return 0;
}
