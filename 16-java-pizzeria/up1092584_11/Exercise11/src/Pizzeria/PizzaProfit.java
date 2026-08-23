package Pizzeria;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Collections;
import java.util.Comparator;
import enums.Location;
import enums.StateOfOrder;
import orderPacket.OrderClass;


// well C might have a had a massive impact on me.. That's why I am using arraylists ._.

public class PizzaProfit extends Pizzeria
{
	private static int iterator = GUI.GeneralFrame.iterator;
	
	
	public PizzaProfit(ArrayList <OrderClass> orders)
	{
		System.out.println("TestProfit");
		waitingTimes = initialiseHashMap(waitingTimes, iterator);
		decideHowToProcessOrdersConsideringLegislation(orders, waitingTimes);
		numberOfOrdersReceived = orders.size();
		averageWaitingTime = getAverage(waitingTimes);
		
	}
	
	// Παίρνω έναν πίνακα από παραγγελίες
	// κάνω loop γιατί είναι FIFO
	
	
	@Override
	public synchronized void decideHowToProcessOrdersConsideringLegislation(ArrayList <OrderClass> orders, HashMap<Integer,Integer> waitingTimes)
	{
		int index = 0;
		Location loc = null;
		
		
		Collections.sort(orders, new Comparator<OrderClass>() // sorts the array based on the values of orders-profit
		{ // thanks open ai for this
            @Override
            public int compare(OrderClass o1, OrderClass o2)
            {
                return o1.getRevenue(o1.getListOfSelectedIngredients()) - o2.getRevenue(o2.getListOfSelectedIngredients()); //not clean code ik
            }
        });
		
		//μαζεύεται πολύ ίδιος κώδικας μαζί...
		
		for(OrderClass order: orders) // for σε for .-. I know..
		{
			System.out.println("TestProfit2");
			System.out.println("TestProfit3");			
			
			int timeForEachOrder = decideWaitingTimeForDelivery(order.location);
			int orderNumber = waitingTimes.get(index);
			order.state = StateOfOrder.toBeDelivered;
			if (timePassed +  decideWaitingTimeForDelivery(order.location) < timeToClose) // The delivery man may deliver the order but there is a chance the shop will close
																				// before he arrives back
			{
				order.state = StateOfOrder.beingDelivered;
				//order.state = StateOfOrder.completed;
			}
			else
			{
				System.out.println("Profit HAS CLOSED");
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
}