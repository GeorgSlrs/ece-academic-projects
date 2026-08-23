package Pizzeria;

import java.util.ArrayList;
import java.util.HashMap;
import enums.Location;
import orderPacket.OrderClass;

public abstract class Pizzeria
{
	protected double numberOfOrdersReceived = 0;   
	protected double numberOfOrdersToBeDelivered = 0;
	public int revenue = 0; // θα το έβαζα double, ωστόσο προέκυψε πρόβλημα με τα αρχεία
	public int timePassed = 0;
	public static final int timeToClose = 1440;
	public HashMap<Integer,Integer> waitingTimes = new HashMap<Integer,Integer>();
	public ArrayList <Integer> minWaitingTimes = new ArrayList<Integer>(); //min waiting times = depends from the location of each order
	public ArrayList <Integer> maxWaitingTimes = new ArrayList<Integer>(); // 2*location_previous + location_currentElement	
	//the hashmap and the 2 arraylists not static beacause we must they must be discrete for each class which extends this
	public double averageWaitingTime = 0; // trying to avoid static..
	
	public abstract  void decideHowToProcessOrdersConsideringLegislation(ArrayList <OrderClass> orders, HashMap<Integer,Integer> waitingTimes);
	
	
	
	protected  HashMap<Integer, Integer> initialiseHashMap (HashMap<Integer, Integer> waitingTimeForOrders, int iter)
	{
		for (int i =0; i < iter; i++)
		{
			waitingTimeForOrders.put(i, 0);
		}
		
		return waitingTimeForOrders;
	}
	

	protected int decideWaitingTimeForDelivery(Location loc)
	{
		if (loc == Location.LOCATION_A)
		{
			return 5;
		}
		else if (loc == Location.LOCATION_B)
		{
			return 10;
		}

		else if (loc == Location.LOCATION_C)
		{
			return 15;
		}
		
		else return -1;
	}
	
	public int getAverage(HashMap<Integer, Integer> waitTimes)
	{
		int avgWaitingTime = 0;
		int i = 0;
		for(i = 1; i <= waitTimes.size(); i++)
		{
			avgWaitingTime += waitTimes.get(i);
		}
		
		avgWaitingTime = avgWaitingTime / i;
		return avgWaitingTime;
	}
	
	
}