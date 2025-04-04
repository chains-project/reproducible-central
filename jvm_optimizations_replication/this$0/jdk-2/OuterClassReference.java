public class OuterClassReference {

    int l;

    void main() {
        new Temp(1) {
            {
                System.err.println(l);
            }
        };
    }
    
}

class Temp {
    int val;

    Temp(int val) {
        this.val = val;
    }
}
