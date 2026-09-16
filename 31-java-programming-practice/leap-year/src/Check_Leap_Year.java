import java.util.Scanner;

public class Check_Leap_Year {
	public static void main(String args[])
	{
		Scanner s = new Scanner(System.in);
		System.out.print("Enter any year: ");
		int year = s.nextInt();
		boolean leap = false;
		if (year % 400 == 0)
		{
			leap = true;
		}
		else if (year % 100 == 0)
		{
			leap = false;
		}
		else if (year % 4 == 0)
		{
			leap = false;
		}
		else
		{
			leap = false;
		}
		if(leap)
		{
			System.out.println("Year " + year + " is a Leap year");
			
	
		}
		else
		{
			System.out.println("Year " + year + " is not a  Leap year");
		}
		}

}
