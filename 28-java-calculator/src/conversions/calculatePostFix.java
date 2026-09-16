package conversions;

import java.util.Stack;

public class calculatePostFix
{
	private Stack<String> postFix;
	private Double result;
	
	
	calculatePostFix(Stack<String> postfix)
	{
		this.postFix = postfix; // the assignment to variable postFix has no effect???????????
		System.out.println("Postfix " + this.postFix);
		result = this.calculateExpression(result,postFix);
		
	}
	
	private Double calculateExpression(Double res, Stack<String> e) 
	{
		//λογικά η st δημιουργείται εδώ μέσα..
		// μα είναι κενή πώς μπορεί να δημιουργείται εδώ μέσα;
		// άμα έχω numeric
		// διάλογος με εαυτό
		Stack <Double> st = new Stack<Double>();
		if(postFix.isEmpty()) 
		{
			return res;
		}
		postFix.forEach(elem -> { //loops through the entire stack
		  switch(elem) 
			{
			case("+"):
			{
				st.push(st.pop() + st.pop());
			}
			case("-"):
			{
				Double tmp = st.pop();
				st.push(st.pop() - tmp); // στις διαφάνειες είχε από πάνω tmp και εδώ d1 oπότε μάλλον βάζουμε το tmp
			}
			case("*"):
			{
				st.push(st.pop() * st.pop()); // επίσης λάθος στις διαφάνειες: έχει + αντί για *
			}
			case("/"):
			{
				Double tmp = st.pop();
				if(Double.valueOf(tmp)!=0)
				{
			st.push(st.pop() / tmp); // τι θα γίνει στην περίπτωση που έχω πολλά δεκαδικά ψηφία;;
				}
			}
			case("^"):
			{
				Double tmp = st.pop();
				st.push(Math.pow(st.pop(), tmp)); // λάθος στη θέση του tmp είναι το x και το tmp δε χρησιμοποιείται
			}
			
			default:
			{
				if (isNumeric(elem))
				{
					st.push(Double.parseDouble(elem));
				}
			}
			
		  }
		});
		res = (double)  Math.round(res * 1000) / 1000; //αφού θέλω στρογγυλοποίηση στα χιλιοστά
		return res;
		
	}
	
	public static boolean isNumeric(String strNum) // εάν δεν πετάξει exception σημαίνει ότι έχουμε numeric.
	{
	    if (strNum == null)
	    {
	        return false;
	    }
	    try
	    {
	        double d = Double.parseDouble(strNum);
	    } catch (NumberFormatException nfe)
	    {
	        return false;
	    }
	    return true;
	}

}