package employee;

abstract public class Academic extends Employee // πρέπει να είναι abstract για να υλοποιείται η printStatistics()
{
	static final int BaseMonthlySalary = 500;
	private int ID;
	
	public Academic(int ID)
	{
		this.ID = ID;
	}
	
	public int returnID ()
	{
		return ID;
	}
	
	public int CalculateMonthlySalary()
	{
		return BaseMonthlySalary;
	}
	
	

}
