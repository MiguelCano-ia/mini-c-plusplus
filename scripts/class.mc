class Animal {
    private:
        int edad;
        float peso;
    public:
        Animal() {
            edad = 5;
            peso = 1.0;
            int counter = 0;
        }

    void setEdad(int e) { edad = e; }
    int getEdad() { return edad; }
    void setPeso(float p) { peso = p; }
    float getPeso() { return peso; }
};

int main() {
    Animal gato;
    gato.setEdad(2);
    gato.setPeso(4.5);
    return 0;
}