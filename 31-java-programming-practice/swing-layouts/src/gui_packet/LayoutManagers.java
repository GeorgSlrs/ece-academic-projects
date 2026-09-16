package gui_packet;

import java.awt.FlowLayout;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;


public class LayoutManagers
{
	public static void main(String[] args)
	{
		JFrame frame = new JFrame ("Sus");
		frame.setSize(200, 300);
		frame.setResizable(true);
		frame.setDefaultCloseOperation(0);
		frame.setFocusable(false);
		
		JButton button1 = new JButton ("oof1");
		JButton button2 = new JButton ("oof2");
		
		JPanel panel1 = new JPanel();
		JPanel panel2 = new JPanel();
		
		panel1.add(button1);
		panel2.add(button2);
		
		frame.add(panel1);
		frame.add(panel2);
		
		frame.setVisible(true);
		
		frame.setLayout(new FlowLayout());
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		
	}
}
