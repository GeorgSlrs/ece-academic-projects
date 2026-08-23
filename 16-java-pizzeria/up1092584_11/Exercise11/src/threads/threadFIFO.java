package threads;
import Pizzeria.PizzaFIFO;
import GUI.*;


public class threadFIFO implements Runnable
{
	public static PizzaFIFO fifo;
	@Override
	public void run()
	{
		PizzaFIFO fifo = new PizzaFIFO(GeneralFrame.orders);
		System.out.println("oof");
		
	}
	
	public static PizzaFIFO  returnInstance()
	{
		return fifo;
	}
	
	

}