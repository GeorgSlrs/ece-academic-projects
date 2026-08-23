package orderPacket;

import enums.*;

import java.util.ArrayList;
import java.security.SecureRandom;

public class OrderClass
{
	protected ArrayList<String> ingredients = new ArrayList<String>();
	protected ArrayList<String> selectedIngredients = new ArrayList<String>();
	protected int cost = 5;
	public  StateOfOrder state = StateOfOrder.inPreparation;
	public  Location location = null;
	public OrderClass()
	{
		ingredients = initialiseIngredients(ingredients);
		selectedIngredients = addRandomSelectedIngredients(selectedIngredients, ingredients);
		this.location = setLocationOfOrder();
		cost += calculateCostOfPizza(selectedIngredients);
	}
	
	private int calculateCostOfPizza(ArrayList<String> selectedIngredients)
	{
		return 5 + 2*selectedIngredients.size();
	}
	
	private ArrayList<String> initialiseIngredients(ArrayList<String> ingredients_ar) //just in case we add more ingredients
	{
		ingredients_ar.add("olives");
		ingredients_ar.add("onions");
		ingredients_ar.add("pineapple");
		ingredients_ar.add("peperoni");
		ingredients_ar.add("chicken");
		ingredients_ar.add("ham");
		ingredients_ar.add("sausage");
		return ingredients_ar;

	}
	
	// yes if we have let's say 5000 orders this method will be executed 5000 times...
	// but I have constructed the program in such a way that I cannot think of any other way
	// without changing many lines
	// we can have a class that is extended by this class but e only need that for the above method..
	protected ArrayList<String> addRandomSelectedIngredients(ArrayList<String> selectedRandomIngredients, ArrayList<String> ingredients)
	{
		int size = 1;
		int index;
		int i = 0;
		String elem;
		SecureRandom rand1  = new SecureRandom();
		size += rand1.nextInt(7); // create a random sized array-random size of order
		
		for (i = 0; i < size; i++)
		{
			index = rand1.nextInt(7);
			elem = ingredients.get(index);  // get a random element from the ingredients
			selectedRandomIngredients.add(elem);	// this way we have a random order
		}
		
		return selectedRandomIngredients;
	}
	
	private Location setLocationOfOrder()
	{
		SecureRandom rand2  = new SecureRandom();
		return Location.values()[rand2.nextInt(Location.values().length)]; // sets a 'random' location for the order
	}
	
	public Location getLocationOfOrder()
	{
		return this.location;
	}
	
	public int getRevenue (ArrayList<String> selectedRandomIngredients)
	{
		return 5 + 2*selectedRandomIngredients.size();
	}
	
	public  ArrayList<String> getListOfSelectedIngredients()
	{
		return selectedIngredients;
	}
}