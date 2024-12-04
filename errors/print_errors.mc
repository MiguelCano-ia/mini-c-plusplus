int main(){

    int edad = 25;
    float promedio = 89.5;
    string nombre = "Alice";
  // Error: falta un argumento
    printf("Edad: %d, Promedio: %f, Nombre: %s\n", edad, promedio);

    // Error: argumento de tipo incorrecto (edad es int, pero se espera float)
    printf("Edad: %f\n", edad);
  return 0;
}