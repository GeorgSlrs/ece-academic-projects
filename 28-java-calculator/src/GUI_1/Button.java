package GUI_1;


import java.awt.Color;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.JButton;
import javax.swing.border.Border;
import javax.swing.border.LineBorder;
import java.awt.Font;
import mainPacket.MainClass;

public class Button extends JButton implements ActionListener
{
	
	
		/**
	 * 
	 */
	private static final long serialVersionUID = -3280258846351583530L;

		Button(String text)
		{
			this.setFocusable(true);
			addActionListener(this);
			makeButton(text);
			// και τώρα αρχίζουμε να μυρίζω τα νύχια μου..
			// γιατί δε γίνoνται τα σωστά χρώματα στο background;;;;;
		}

		
		
		// εδώ δε γιατί δε γίνεται κάτι;;;;;;;;;;;;;;;;;;;;;;
	@Override
	public void actionPerformed(ActionEvent e) // θα μπορούσα να το κάνω και αλλίως
	// σε κάθε κλάση button_type1, button_type2, button_type3 (1-αριθμοί, 2-πράξεις, 3-C, (, )
	// έτσι ώστε να αποφύγω τα if-else αλλά πάλι αυξάνεται ο όγκος του κώδικα, εφαρμόζω όμως καλύτερα
	// το αντικειμενοσταφές μοντέλο
	{
		JButton button = (JButton) e.getSource(); // πατήθηκε το κουμπί
		
		if (button.getName() == "c") // δουλεύει-δεν πετάει exceptions στο console με το ==, με το .equals δε δουλεύει
		{
			MainClass.Calculator.clear();
		}
		
		else if (button.getName() == "=")
		{
			MainClass.Calculator.doOperationsInitial();
		}
		
		else
		{
			MainClass.Calculator.addText(button.getName());
			
		}
	}
	
	private void makeButton(String text)
	{
		//δε λειτουργεί καθόλου απ'ό,τι φαίνεται αυτή η μέθοδος.. ._.
		
		this.setText(text);
		this.setBorderPainted(false);
		this.setOpaque(true);
		Border border2 = new LineBorder(Color.RED, 4, true);
		this.setBorder(border2);
		this.setBackground(Color.GREEN);
		this.setBackground(Color.BLACK);
		this.setFont(new Font("Arial", Font.BOLD, 19)); 
		this.setContentAreaFilled(false);
		this.setVisible(true);
	}

}