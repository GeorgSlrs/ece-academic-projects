package GUI_1;

import javax.swing.JFrame;
import javax.swing.JTextField;

import conversions.*;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.GridLayout;
import javax.swing.JPanel;

public class CalculatorFrame extends JFrame
{
	
	/**
	 * 
	 */
	private static final long serialVersionUID = -5328309024324910928L;
	public static JTextField textField= new JTextField();
	
	 public CalculatorFrame()
	 {
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		this.setVisible(true);
		this.setLayout(new BorderLayout());
		this.setTitle(":(");
		this.setBackground(Color.GRAY);
		this.setSize(300,300);
		this.setResizable(false);
		this.add(textField, BorderLayout.NORTH);
		this.add(createPanel());
		this.setVisible(true);
	}
	
	
	private JPanel createPanel()
	{
		JPanel calcPanel = new JPanel();
		calcPanel.setLayout(new GridLayout(5,4));
		// για να το αποφύγω αυτό θα μπορούσα να έχω μία κλάση button με ιδιότητες
		// χρώμα, εικονίδιο
		// μετά να έχω 3 κλάσεις που την κάνουν extend
		// 1 κλάση των αριθμών
		// 1 κλάση των πράξεων
		// μία κλάση για τα C, (, )
		//Το πλεονέκτημα είναι ότι εφαρμόζω ένα καλύερο αντικειμενοστραφές μοντέλο
		// ωστόσο θα αυξηθεί ο όγκος του κώδικα
		calcPanel.add(new Button("c"));
		calcPanel.add(new Button("("));
		calcPanel.add(new Button(")"));
		calcPanel.add(new Button("/"));
		calcPanel.add(new Button("7"));
		//////////////////////////////
		calcPanel.add(new Button("8"));
		calcPanel.add(new Button("9"));
		calcPanel.add(new Button("*"));
		calcPanel.add(new Button("4"));
		calcPanel.add(new Button("5"));
		///////////////////////////////
		calcPanel.add(new Button("6"));
		calcPanel.add(new Button("-"));
		calcPanel.add(new Button("1"));
		calcPanel.add(new Button("2"));
		calcPanel.add(new Button("3"));
		///////////////////////////////
		calcPanel.add(new Button("+"));
		calcPanel.add(new Button("0"));
		calcPanel.add(new Button("^"));
		calcPanel.add(new Button("*"));
		calcPanel.add(new Button("="));
		
		return calcPanel;
	}
	
	public  void clear()
	{
		textField.setText("");
	}
	public void addText(String text)
	{
		if(text == null)
		{
			System.out.println("NULL TEXT"); //why null text bruh
			
		}
		textField.setText(text + textField.getText()); // εμφανίζει null στην οθόνη great
	}
	
	public  void doOperationsInitial()
	{
		String expr = textField.getText();
		infixToPostFix txt = new infixToPostFix(expr); // oκ καλώ τον κατασκευαστή γιατί όμως δεν τυπώνονται κάποια πράγματα;;
		System.out.println("PostFix: " + txt);
		
		
	}
}
