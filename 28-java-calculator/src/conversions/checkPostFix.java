package conversions;

//check for
// ()
// ++


import java.util.Stack;

// κανονικά θα έπρεπε να πετάει διάφορα Exceptions but oof..

public class checkPostFix
{ // ναι κανονικά θα έπρπε να έχει άλλο όνομα..
	private Stack <String> inFixExp = new Stack<String>();
	private int cnt = 0;
	private int i = 0;
	private  String prev = "";
	
	public checkPostFix(Stack <String> infixExp)
	{
		this.inFixExp = infixExp;
	}
	
	public void correct()
	{
		String error = "false";
		//String prev = "";
		Stack<Integer> counters = new Stack<Integer>();
		inFixExp.forEach(elem -> {
			
			
			if (elem.equals(")") && prev.equals("("))
			{
				//throw new Exception("Empty expression in parenthesis");
				System.out.println("Empty expression in parenthesis");
			}
			
			while(isOp(inFixExp.get(i)))
			{
				cnt ++;
				i++;
			
			}
			
			counters.push(cnt);
			cnt= 0;
			
			if (isOp(prev) && (! (isNumeric(elem) || elem.equals("(") || elem.equals(")"))))
			{
				System.out.println("Error bruh");
			}
				
			if (elem.equals("(") && (! (isOp(prev) || prev.equals("("))))
			{
				System.out.println("Again wrong exp");
			}
			prev = elem; //Local variable prev defined in an enclosing scope must be dec
			//lared final or effectively final??
			
		});
		checkStack(counters); 
		// εδώ η ιδέα είναι η εξής
		// loop στο infix
		//αν βρεθούν διαδοχικά >1 τελεστές
		// τότε έχω λάθος
		// αν όχι πηγαίνω στο επόμενο στοιχείο και ακολουθώ την ίδια διαδικασία
		//
		i = 0;
		if(counter("(") != counter(")"))
		{
			System.out.println("Not enough ( or )");
		}
		
	}
	
	private void checkStack(Stack<Integer> st)
	{
		int i = 0;
		for (i = 0; i < st.size(); i++)
		{
			if (st.get(i) > 1)
			{
				System.out.println("2 or more subsequent operators");
			}
		}
	}
	
	private boolean isOp(String elem)
	{
		if (elem.equals("+") || elem.equals("-") || elem.equals("*") || elem.equals("/") || elem.equals("^"))
		{
			return true;
		}
		return false;
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
	// ή θα μπορούσαμε να το κάνουμε με extend

	private int counter(String ch)
	{
		int cnt2 = 0;
		for(int i = 0; i <inFixExp.size(); i++)
		{
			if(inFixExp.get(i).equals(ch))
			{
				cnt2++;
			}
		}
		return cnt2;
	}
}