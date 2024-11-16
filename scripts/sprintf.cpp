//Preuba con sprintf

int main() {
    int edad = 25;
    float promedio = 89.5;
    string nombre = "Alice";

    string buffer;
    sprintf(buffer, "Edad: %d, Promedio: %f, Nombre: %s\n", edad, promedio, nombre);

    printf("%s", buffer);
    
    return 0;
}