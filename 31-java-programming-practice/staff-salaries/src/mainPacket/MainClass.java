package mainPacket;

//TODO in mainclass: 1- 100k obljects 2- search with hashmap and linked list 3-append node in CreateRandomEmployee
//import java.util.Random; for version 2//
import employee.*;
import enumerations.StaffType;
import exceptions.InvalidWorkingHours;
import randomize.Randomize;


// πρόβλημα που το βρήκα τώρα φαίνεται ότι κάνει skip κάποια loops (στην εργασία της 4ης εβδομάδας, δε ξέρω γιατί //
// το excpetion δεν εμφανίζεται..
//1-loop
//2-Δημιουργίσ PermanentHourlyBased
//3- Έλεγχος για τον κάθε τύπο
//4- Δημιουργία αντίστοιχων αντικειμένων με αντίστοιχες ιδιότητες
public class MainClass{
	//static private double number;
	private static final int NumberofEmployessToBeCreated = 100000; // compile-time constant, static γιατί αφορά την κλάση συνολικά
	public static void main(String[] args) 
	{
		CreateRandomEmployee(NumberofEmployessToBeCreated);
		Employee Employee_to_be_searched1 = Employee.search_with_linkedList (34324);
		Employee Employee_to_be_searched2 = Employee.search_with_Hashmap(54354);
		Employee_to_be_searched1.printStatistics();
		Employee_to_be_searched2.printStatistics();
		
	}
	public static void CreateRandomEmployee (int NumberOfEmployeesToBeCreated) // Άμα έβαζα ότι εμφάνιζε exception μου πέταγε λάθος
	{
		System.out.println("The program has begun creating: "+ NumberOfEmployeesToBeCreated + " Random Employees"); // Δε μπορώ να χρησιμοποιήσω το this εδώ
		for(int i=1; i <= NumberOfEmployeesToBeCreated; i++) 
		{
			StaffType type_staff=Randomize.Staff();
			if (type_staff == StaffType.Permanent)
			{
				PermanentStaff perm = new PermanentStaff(i);
				perm.CalculateMonthlySalary();
				Employee.addEmployeeNode (perm);
			}
			// έλεγχος για exception
			if (type_staff == StaffType.Permanent)
			{
				HourlyStaff hour_staff = new HourlyStaff(i);
				try {
					hour_staff.setWorkedHours(Randomize.MonthlyWorkingHours());
					hour_staff.CalculateMonthlySalary();
					Employee.addEmployeeNode (hour_staff);
				}
				catch (InvalidWorkingHours exc)
				{
					System.out.println(exc.getMessage());
					System.exit(0);
				}
			}
			//number ++;
		}
		
		
		
		//System.out.println("Number of objects: " + number);
	}
}

