package gui_packet;

import javax.swing.*;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.BorderLayout;


public class ex4 {
	
	public static void main(String[] args) {
		
	JFrame frame1 = new JFrame("Exercise1");
	JPanel panel1 = new JPanel();
	JLabel label1 = new JLabel("Hello");
	
	
	frame1.setSize(800, 800);
	frame1.setVisible(true);
	frame1.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
	frame1.setLayout(new BorderLayout(10, 10));
	
	panel1.setPreferredSize(new Dimension(100,100));
	panel1.setBackground(Color.BLACK);
	
	label1.setFont(new Font("Arcade Classic", Font.PLAIN, 25));
	label1.setForeground(Color.ORANGE);
	
	panel1.add(label1);
	frame1.add(panel1, BorderLayout.NORTH);

	
	frame1.setFocusable(true);
	frame1.setResizable(true);
	frame1.setVisible(true);
	
	
	
	
	}
	
	
	
	
	
	

}
