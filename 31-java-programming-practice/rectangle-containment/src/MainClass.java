// Πώς να έχω το όνομα week1 και το όνομα της κλάσης να είναι MainClass;
// New project???
import java.util.Scanner;

public class MainClass {
	public static void main(String[] args) {
		Scanner in = new Scanner(System.in);
		System.out.println("Give x cor: ");
		float x = in.nextFloat();
		System.out.println("Give y cor: ");
		float y = in.nextFloat();
		System.out.println("Give width: ");
		float wid = in.nextFloat();
		System.out.println("Give height: ");
		float hei = in.nextFloat();
		Rectangle new_Rec = new Rectangle(x, y, wid, hei);
		
		
		System.out.println("Give x coordinate to see if the point is inside the rectangle: ");
		float search_x = in.nextFloat(); // Έτσι μου την έβγαλε αυτήν τη μέθοδο
		System.out.println("Give y coordinate to see if the point is inside the rectangle: ");
		float search_y = in.nextFloat();
		
		if(new_Rec.contains(search_x, search_y))
			System.out.println("The point you gave is inside the rectangle you created before");
		else System.out.println("Not inside");
		
		
		
		in.close(); // Moυ έβγαλε warning αν δε το έβαζα αυτό..
				
		
	}

}
