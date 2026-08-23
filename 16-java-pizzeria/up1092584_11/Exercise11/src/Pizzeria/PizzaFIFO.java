package Pizzeria;

import java.util.ArrayList;
import orderPacket.OrderClass;
import java.util.HashMap;



//minwaiting time based on location
//max waiting time: 2current_order location + order_location
import enums.*;
public class PizzaFIFO extends Pizzeria 
{
	
	private static int iterator = GUI.GeneralFrame.iterator;
	
	
	// create a
	public PizzaFIFO(ArrayList <OrderClass> orders)
	{
		System.out.println("TestFIFO");
		waitingTimes = initialiseHashMap(waitingTimes, iterator);
		decideHowToProcessOrdersConsideringLegislation(orders, waitingTimes);
		numberOfOrdersReceived = orders.size();
		averageWaitingTime = getAverage(waitingTimes);
		
	}
	
	// Παίρνω έναν πίνακα από παραγγελίες
	// κάνω loop γιατί είναι FIFO
	
	
	@Override
	public synchronized void   decideHowToProcessOrdersConsideringLegislation(ArrayList <OrderClass> orders, HashMap<Integer,Integer> waitingTimes)
	{
		int index = 0;
		Location loc = null;
		
		for(OrderClass order: orders) // for σε for .-. I know..
		{
			System.out.println("TestFIFO2");
			System.out.println("TestFIFO3");
			int prevTimeForEachOther = 0;
			int timeForEachOrder = decideWaitingTimeForDelivery(order.location);
			int orderNumber = waitingTimes.get(index);
			//timePassed += 2 *protected int decideWaitingTimeForDelivery(Location loc);
			order.state = StateOfOrder.toBeDelivered;
			if (timePassed +  decideWaitingTimeForDelivery(order.location) < timeToClose) // The delivery man may deliver the order but there is a chance the shop will close
																				// before he arrives back
			{
				order.state = StateOfOrder.beingDelivered;
				//order.state = StateOfOrder.completed;
			}
			else
			{
				System.out.println("FIFO HAS CLOSED");
				break;
			}
			for (int i = index; i < index; i++)
			{
				orderNumber += timeForEachOrder; 
			}
			waitingTimes.put(index, orderNumber);	/////////
			index ++;
			revenue += order.getRevenue(order.getListOfSelectedIngredients());
			System.out.println(timePassed);
			minWaitingTimes.add(timeForEachOrder);
			maxWaitingTimes.add(2*timeForEachOrder + prevTimeForEachOther);
			timePassed += decideWaitingTimeForDelivery(order.location);
			prevTimeForEachOther = timeForEachOrder;
			//orders.remove(index);
			
		}
		
		
	}		
}