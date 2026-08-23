package threads;

import Pizzeria.PizzaFIFO;
import Pizzeria.PizzaProfit;
import GUI.*;


public class threadProfit implements Runnable
{	
	public static PizzaProfit profit;

	
	@Override
	public void run()
	{
		PizzaProfit profit = new PizzaProfit(GeneralFrame.orders);
		
	}
	
	
	public static PizzaProfit  returnInstance()
	{
		return profit;
	}

}