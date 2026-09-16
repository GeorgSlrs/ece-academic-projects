package gui_packet;

import java.awt.FlowLayout;
import javax.swing.*;


public class MyFrame
{
	public static void main (String[] args) {
		JFrame frame = new JFrame("Test Frame");
		frame.setSize(600, 500);
		frame.setVisible(true);
		
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setLayout(new FlowLayout (FlowLayout.LEFT, 10, 20));
		
		frame.add(new JLabel("Amogus"));
		frame.add(new JTextField(10));
		frame.add((new JLabel("Sussy Baka")));
		frame.add(new JTextField(1));
		frame.add(new JLabel ("Last Name"));
		frame.add(new JTextField(9));
		
		
	}
}
