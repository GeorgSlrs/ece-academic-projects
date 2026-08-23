package Pizzeria;

import java.util.ArrayList;
import java.util.HashMap;

import enums.Location;
import enums.StateOfOrder;
import orderPacket.OrderClass;
import java.util.Collections;

public class PizzaRandom extends Pizzeria
{
	private static int revenueOne = 0;
	private static int iterator = GUI.GeneralFrame.iterator;

	
	public PizzaRandom(ArrayList <OrderClass> orders)
	{
		System.out.println("TestRandom");
		waitingTimes = initialiseHashMap(waitingTimes, iterator);
		orders = shuffleArray(orders);
		decideHowToProcessOrdersConsideringLegislation(orders, waitingTimes);
		averageWaitingTime = getAverage(waitingTimes);
	}
	
	@Override
	// ίσως επειδή είναι κοινή η μέθοδος θα μπορούσα να την έχω υλοποιημένη στην 	Pizzeria
	public synchronized void decideHowToProcessOrdersConsideringLegislation(ArrayList <OrderClass> orders, HashMap<Integer,Integer> waitingTimes)
	{
		int index = 0;
		Location loc = null;
		
		for(OrderClass order: orders) // for σε for .-. I know.. O(n^2) oof
		{
			System.out.println("TestRandom2");
			System.out.println("TestRandom3");
			int timeForEachOrder = decideWaitingTimeForDelivery(order.location);
			int orderNumber = waitingTimes.get(index);
			//timePassed += 2 *protected int decideWaitingTimeForDelivery(Location loc);
			order.state = StateOfOrder.toBeDelivered;
			if (timePassed +  decideWaitingTimeForDelivery(order.location) < timeToClose) // The delivery man may deliver the order but there is a chance the shop will close
																				// before he arrives back
			{
				order.state = StateOfOrder.beingDelivered;
				numberOfOrdersToBeDelivered ++;
				//order.state = StateOfOrder.completed;
			}
			else
			{
				System.out.println("Random HAS CLOSED");
				break;
			}
			for (int i = index; i < index; i++)
			{
				orderNumber += timeForEachOrder; 
			}
				
			index ++;
			revenue += order.getRevenue(order.getListOfSelectedIngredients());
			System.out.println(timePassed);
			timePassed += decideWaitingTimeForDelivery(order.location);
			//orders.remove(index);
			
		}
		
		
	}
	
	private ArrayList <OrderClass> shuffleArray(ArrayList <OrderClass> orders)
	{
		 Collections.shuffle(orders);
		 return orders;
	}
}