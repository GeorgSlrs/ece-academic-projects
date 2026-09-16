package employee;

import enumerations.WorkingExperience;
import randomize.Randomize;
import exceptions.InvalidWorkingHours;

final public class HourlyStaff extends Academic // αφού την υλοποιοεί την printStatistics γιατί πετάει error;;;;;;;;;;;;;;;;;;;
// edit: wow turns out to be a misspeling of the word Statistics (wrote printStatisti-scs instead of printStatisti-cs -_-
{
	private WorkingExperience experience;
	private int workedhours = 0;
	//private int MonthlySalary = 0;//
	private static final int MaxWorkHours = 40;
	
	
	public HourlyStaff (int ID)
	{
		super(ID);
		experience = Randomize.WorkingExperience();
	}
	
	public void setWorkedHours(int workedhours) throws InvalidWorkingHours 
	{
			// workedhours = Randomize.MonthlyWorkingHours(); //
			if (workedhours > 40) throw new InvalidWorkingHours("Maximum hours of work surpassed.Exception.Maximum working hours: " + MaxWorkHours);
			else
			{
				this.workedhours = workedhours;
			}
	}
	
	
	@Override
	// Θα μπορούσα να μην έχω μεταβλητές στα if και να κάνω επιστροφή κατευθείαν τον συνολικό μισθό
	// αλλά για κάποιο λόγο μου πέταγε λάθος..
	public int CalculateMonthlySalary() 
	{
		int extraSalary = 0;
		if(experience == WorkingExperience.uptoFiveYears)
		{

			extraSalary = (workedhours * 10);
		
		}
		
		if(experience == WorkingExperience.FiveToTenYears)
		{

			extraSalary = (workedhours * 20);
		
		}
		
		if(experience == WorkingExperience.morethanTenYears)
		{

			extraSalary = (workedhours * 30);
		
		}
		return extraSalary + BaseMonthlySalary;
		

	}
	
	public void printStatistics()
	{
		System.out.println("\n\n\n");
		System.out.println("Employee with ID:   " + returnID());
		System.out.println("Type of employee:   HourlyBased");
		System.out.println("Working hours as an hourly Employee (if It's 0 then there was an exception):   " + workedhours);
		System.out.println("Total Salary as an hourly employee:   " + CalculateMonthlySalary());
		System.out.println("Total Experience:   " + experience);
	}
}
