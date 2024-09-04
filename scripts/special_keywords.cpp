class Base {
public:
    void display() {
        printf("Base class\n");
    }
};

class Derived : public Base {
public:
    void display() {
        Base::display();  
        printf("Derived class\n");
    }
};

int main() {
    Derived* obj = new Derived(); 
    obj->display();
    delete obj; 
    return 0;
}