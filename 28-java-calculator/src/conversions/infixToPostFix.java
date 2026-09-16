package conversions;
// comments go oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooff

import java.util.Stack;
import java.util.Iterator;
// αρνητικοί -> προσθέτω ένα +0
// -4 -> 0-4
// αλλά άμα θέλω δεκαδικούς;;;
// αυτό που μπορώ να κάνω είναι να πάρω τον αριθμό των ψηφίων μετά την υποδιαστολή
// να τα μετρήσω και μετά να βάλω στη στοίβα το ακέραιο μέρος προσθέτοντας σε αυτό
// τον αριθμό μετά την υποδιαστολή διαιρεμένο με το 10^πλήθος_ψηφίων_μετά_την_υποδιαστολή
// αρκετά φιλόδοξο .-.
// για μία στιγμή αυτό δεν έχει ήδη γίνει στην εργασία 9;
// constructor of BrainClass.java overloaded...
public class infixToPostFix
{
	protected Stack <String> infixExp = new Stack<String>();
	//Stack <String> operators = new Stack<String>();
	protected Stack <String> postFix = new Stack<String>();
	private String expression;
	//private String infixToPostFixStr;
	
	
	 public infixToPostFix(String expression)
	{
		this.expression = expression;
		getinfixExp(expression);
		getPostfixExp();
		System.out.println("Entered");
		System.out.println("Infix: "+ infixExp);
		System.out.println("Postfix: "+ postFix);
		
		
	}
	
	private void getinfixExp(String exp)
	{
		// Πρέπει να βρω τρόπο έτσι ώστε να έχω και δεκαδικούς αλλά και αριθμούς > 1 ψηφίου
		// Μία λύση θα ήταν να έχω μία βοηθητική μεταβλητή και όταν συναντάω την επόμενη φορά αριθμό/. 
		// να το προσθέτω σε αυτή τη βοηθτική μεταβλητή
		// και μετά να καθαρίσω αυτή τη μεταβλητή εάν βρω οperator
		// θεωρώ καλοπροαίρετο χρήστη
		// εδώ θα πάρω τη λύση που προσφέρεται γιατί δε δουλεύει με την καμία
		int i =0;
		String helpVar = "";
		char prev =  '\0'; // '''
		char currentCharacter;
		//String currentString;
		for (i = 0; i < exp.length(); i++)
		{
			currentCharacter = exp.charAt(i);
			//currentString = Character.toString(currentCharacter);
			// θα πρέπει να έχω  μία μεταβήτή πο να βλέπει το προηγούμενο στοιχείο
			
			if (currentCharacter == '.' || Character.isDigit(currentCharacter))
			{
				helpVar += Character.toString(currentCharacter);
				
			}
			
			else {
				if (helpVar != "") {
					infixExp.push(helpVar); // apparently this works
				}
				
				if(
						(currentCharacter == '-' && prev == '\0') || //note to self string == null x
						(currentCharacter == '-' && prev == '(') ||
						(currentCharacter == '+'&& prev == '\0') ||
						(currentCharacter == '+' && prev == '(') 
						)
				
					{
						infixExp.push("0");
					}
				
				infixExp.push(Character.toString(currentCharacter)); // apparently this works .-.
				helpVar = "";
			}
			prev = currentCharacter; // linked lists flashbacks..
		}
	}
	
public Stack<String> returnExpression(Stack<String> x)
	{  //just in case i need it
		return x;
	}
	
	
	private int orderOfOperations(String operator)
	{
		// εδώ δημιουργείται ένα σημαντικό θέμα
		// πχ εάν μπλεχτούν οι τελεστες  χωρίς παρενθέσεις πχ 7*8:5
		// τότε ποια πράξη προηγείται;;
		// θεωρούμε λοιπόν καλοπροαίρετο τον χρήστη
		
		if (operator.equals("+") || operator.equals("-")) return 1;
		else if (operator.equals("*") || operator.equals("/")) return 2;
		else if (operator.equals("^")) return 3;
		else return -1;
		
		
	}
	
	private void getPostfixExp()
	{
		Stack<String> op = new Stack<String>(); //iterate though the infixExp
		//private String infixToPostFixStr;
		//infixExp.forEach(null);
		infixExp.forEach(elem -> {
		{
			if (elem.equals("("))
			{
				op.push(elem);
			}
			
			else if (elem.equals(")"))
			{
				while (!op.peek().equals("("))
				{
					postFix.push(op.pop());
					//infixToPostFixStr += operators.peek();
				}
				op.pop();
				}
				
				
				
				else if ( (elem.equals("+")) ||elem.equals("-") || elem.equals("*") || (elem.equals("^"))) // ναι, οκ θα μπορούσα να το βάλω σε μία συνάρτηση
				{
					if (postFix.isEmpty())
					{
						postFix.push(op.pop());
					
					}
					
					else while(op.size() > 0 && orderOfOperations(elem) <= orderOfOperations(op.peek())){
						postFix.push(op.pop());
					}
			
				}
		}});
					
					
					
					//while(orderOfOperations((String)value.next()) <= orderOfOperations(operators.peek()))
					//{
						
						//postFix.push(operators.pop()); // top element has more precedence than the bottom element so it goes into postFix
						
					//}
					//operators.push((String)value.next()); //current element has more precedence that the top element so it goes into operators stack
					// before going into postFix (including -1 precedence)!!!
					//parenthesises are not considered operators here-wrong
					
				
						
				//else
				//{//}
			//////  αναγκαστικά στο τέλος θα έχω operators...
			//while(!operators.isEmpty())
			//{ // the remaining operators
			//	postFix.push(operators.pop());
			//}
					
		
	}
	
	//public static void printStacks() {
		//System.out.println("Entered");
		//System.out.println("Infix: "+ infixExp);
		//System.out.println("Postfix: "+ postFix);
	//}
}