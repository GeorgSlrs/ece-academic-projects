package employee;

import java.util.HashMap;
import java.util.LinkedList;
//import java.util.Hashmap;

//note to self: δε μπορώ να έχω private σε static μέθοδο!!!!!!!!!!!!
// διότι δε μπορώ να έχω πρόσβαση;
abstract public class Employee
{
	static private HashMap <Integer, Employee> hashmap_list = new HashMap <Integer, Employee>();
	private static LinkedList <Employee> employee_linkedlist = new LinkedList <Employee> ();
	
	abstract public int returnID();
	abstract public void printStatistics();
	
	
	public static void addEmployeeNode (Employee x) //STATIC!!!!
	{
		employee_linkedlist.add(x);
		hashmap_list.put(x.returnID(), x);
	}
	
	public static Employee search_with_Hashmap (int id) // static διότι μπορεί να μη θέλουμε να δημιουργήσουμε ένα αντικείμενο για να την καλέσουμε
	
	{
		double start, duration;
		Employee res;
		start = System.currentTimeMillis();
		res = hashmap_list.get(id);
		duration = System.currentTimeMillis() - start;
		System.out.println("Duration for searching by hashmap " + duration + " ms ");
		return res;
	}
	
	public static Employee search_with_linkedList (int id)
	{
		// θα κάνω loop μέχρι η τιμή που αντιστοιχεί σε ένα κλειδί, το id της (καλώ την returnID ;;) ίσο με το δοσμένο id
		// Θέλω το loop να τρέχει όσο μεγάλη είναι η λίστα 
		//private 
		double start, duration;
		int i = 0;
		int int_res2 = 0;
		Employee search_res = null; // Θέλει αρχικοποίηση
		start = System.currentTimeMillis();
		for (i = 0; i < employee_linkedlist.size(); i++)
		{
			int_res2 = employee_linkedlist.get(i).returnID();
			if (int_res2 == id)
			{
				search_res = employee_linkedlist.get(i);
				break;
			}
		}
		duration = System.currentTimeMillis() - start;
		System.out.println("Time for searching by linked list: " + duration + " ms ");
		
		return search_res; 
	}
	
	
}
