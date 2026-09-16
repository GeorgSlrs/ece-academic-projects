package employee;
import enumerations.Bathmida;
import randomize.Randomize; 

final public class PermanentStaff extends Academic 
{
	private Bathmida rank;
	
	public PermanentStaff(int id) 
	{
		super(id);
		rank = Randomize.Bathmida();
	}
	
	@Override
	public int CalculateMonthlySalary() {
		int mainSalary = 0;
		if(rank == Bathmida.Lecturer)
		{
			mainSalary = 1000;
		}
		
		if(rank == Bathmida.Assistant)
		{
			mainSalary = 1200;
		}
		
		if(rank == Bathmida.Associate)
		{
			mainSalary = 1400;
		}
		
		if(rank == Bathmida.Professor)
		{
			mainSalary = 1500;
		}
		
		return mainSalary + BaseMonthlySalary;
	    }
	
	public void printStatistics()
	{
		System.out.println("\n\n");
		System.out.println("Type of employee:   Permanent");
		System.out.println("Employe id:   " + returnID());
		System.out.println("Rank:   " + rank);
		System.out.println("Total Salary as permanent:   " + CalculateMonthlySalary());				
	}
		
}
