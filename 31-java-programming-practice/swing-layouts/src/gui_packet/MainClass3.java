package gui_packet;
import javax.swing.*;
import java.awt.FlowLayout;

public class MainClass3 extends JFrame{
	MainClass3(){
		JFrame frame = new JFrame("Exercise");
		frame.setSize(600, 800);
		frame.setResizable(true);
		frame.setLayout(new FlowLayout(FlowLayout.LEFT, 10, 20));
		frame.setFocusable(true);
		frame.setVisible(true);
		frame.setDefaultCloseOperation(EXIT_ON_CLOSE);
		
		JLabel button1 = new JLabel("First Name");
		JTextField text1 = new JTextField(8);
		JLabel button2 = new JLabel("Init");
		JTextField text2 = new JTextField(1);
		JLabel button3 = new JLabel("Last Name");
		JTextField text3 = new JTextField(8);
		frame.add(button1);
		frame.add(text1);
		frame.add(button2);
		frame.add(text2);
		frame.add(button3);
		frame.add(text3);
		
		frame.setVisible(true);
		
		
		
		
		
	}
	
	public static void main(String[] args)
	{
		MainClass3 x = new MainClass3();
	}

}
