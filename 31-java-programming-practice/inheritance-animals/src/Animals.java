

class Animal {
    String name = "animal";

    void makeNoise() {
	System.out.println("βγάζω ήχο");
    }

    public String toString() {
	System.out.println(name);
	return this.name;
    }
}

class Dog extends Animal {
    String name = "dog";

    @Override
    void makeNoise() {
	System.out.println("γαυγίζω...");
    }

    void angryBark() {
	System.out.println("γαυγίζω άγρια...");
    }
}

class BabyDog extends Dog {
    String name = "baby dog";

    @Override
    void makeNoise() {
	System.out.println("κλαψουρίζω...");
    }
//    
//    public String toString() {
//	System.out.println(name);
//	return this.name;
//    }
}

class Cat extends Animal {
    String name = "cat";

    @Override
    void makeNoise() {
	System.out.println("νιαουρίζω...");
    }
}

class Animals {
    public static void main(String args[]) {
	Animal animal = new Animal();
	animal.makeNoise();
	animal.toString();

	System.out.println("----");
	Animal dog = new Dog(); // upcasting: από Dog σε Animal
	dog.toString();
	dog.makeNoise();
//	dog.angryBark(); //downcasting
	((Dog) dog).angryBark(); // downcasting από Animal σε Dog, και κλήση της μεθόδου

	System.out.println("----");
	System.out.println(dog instanceof Animal);
	System.out.println(dog instanceof Dog);
	System.out.println(dog instanceof BabyDog);

	System.out.println("----");
	System.out.println(dog.name);
	System.out.println(((Dog) dog).name);
    }
}