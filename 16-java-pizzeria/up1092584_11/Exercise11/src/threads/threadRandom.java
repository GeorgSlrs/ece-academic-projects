package threads;
import Pizzeria.PizzaRandom;
import GUI.*;


public class threadRandom implements Runnable
{
	public static PizzaRandom random;
	
	
	@Override
	public void run()
	{
		PizzaRandom random = new PizzaRandom(GeneralFrame.orders);
		
	}
	
	
	public static PizzaRandom  returnInstance()
	{
		return random;
	}
	

}