int main(){
  string buffer;
  int edad = 25;
  float promedio = 89.5;
  string nombre = "Alice";



  // Uso incorrecto: el buffer no es declarado
  sprintf(no_declared_buffer, "Edad: %d", edad);

  // Uso incorrecto: tipos incompatibles
  sprintf(buffer, "Edad: %f", edad);
}