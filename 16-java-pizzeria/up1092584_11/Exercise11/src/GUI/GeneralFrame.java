package GUI;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Cursor;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.border.Border;
import javax.swing.border.LineBorder;
import java.util.ArrayList;
import orderPacket.OrderClass;
import Pizzeria.*;
import java.lang.Thread;
import threads.*;


public class GeneralFrame extends JFrame implements ActionListener
{
	private JTextField simTextField = new JTextField(30);
	public static int iterator = 0;
	protected int numberOfOrders;
	public static ArrayList<OrderClass> orders = new ArrayList<OrderClass>();
	public GeneralFrame()
	{
		JButton simButton = new JButton("Start simulation");
		JLabel	simLabel = new JLabel();
		//simTextField.setSize(800,800); 
		configureFrame(simButton, simLabel, simTextField);
		
		
		
		
	}
	
	@Override
	public void actionPerformed(ActionEvent e)
	{
		int i = 0;
		//createRandomOrders
		try {
				numberOfOrders = Integer.parseInt(simTextField.getText());
				System.out.println("Successful");
			}
		catch(NumberFormatException ex)
		{
			System.out.println("Please enter an integer");
			ex.printStackTrace();
		}
		
		for (i = 0; i < numberOfOrders; i++)
		{
			orders.add(new OrderClass());
		}
		
		iterator = i;
		
		Thread thread1 = new Thread(new threadFIFO());
		Thread thread2 = new Thread(new threadProfit());
		Thread thread3 = new Thread(new threadRandom());
		thread1.start();
		thread2.start();
		thread3.start();
		
		//PizzaFIFO fifo = new PizzaFIFO(orders);
		//PizzaRandom random = new PizzaRandom(orders);
		//PizzaProfit profit = new PizzaProfit(orders);
		
	}
	
	public void configureFrame(JButton button, JLabel label, JTextField textfield)
	{
		
		this.setTitle("Pizzeria Simulations");
		this.setDefaultCloseOperation(EXIT_ON_CLOSE);
		this.setLocationRelativeTo(null);
		this.setFocusable(true);
		this.setSize(800,800);
		this.setLayout(new BorderLayout());
		this.add(createButton(button), BorderLayout.CENTER);
		this.add(createLabel(label), BorderLayout.NORTH);
		this.add(createTextField(textfield), BorderLayout.SOUTH);
		
		
		this.setVisible(true);
	}
	
	
	private JPanel createButton(JButton button)
	{
		JPanel panel1 = new JPanel();
		panel1.setBackground(Color.cyan);
		//button.setFont(new Font("Serif", Font.ITALIC, 36)); 
		button.setBackground(null);
		button.addActionListener(this);
		makeBtnsTransparent(button);
		panel1.setVisible(true);
		panel1.setFocusable(true);
		panel1.add(button);
		return panel1;
	}
	
	private void makeBtnsTransparent(JButton btn)
	{
		btn.setBackground(Color.BLACK);
		btn.setOpaque(false);
		btn.setContentAreaFilled(false);
		btn.setFocusPainted( false );
		Border border2 = new LineBorder(Color.RED, 4, true);
		btn.setBorder(border2);
		btn.setFont(new Font("Arial", Font.BOLD, 25));
		btn.setCursor(new Cursor(Cursor.HAND_CURSOR));

	}
	
	private JPanel createLabel(JLabel label)
	{
		JPanel panel2 = new JPanel();
		label.setFont(new Font("Arial", Font.BOLD, 25));
		label.setText("Oof");
		
		panel2.setBackground(Color.red);
		panel2.setVisible(true);
		panel2.setFocusable(true);
		panel2.add(label);
		return panel2;
	}
	
	private JPanel createTextField(JTextField textfield)
	{
		
		JPanel panel3 = new JPanel();
		panel3.setBackground(Color.black);
		Border border2 = new LineBorder(Color.RED, 4, true);
		panel3.setBorder(border2);
		panel3.add(textfield);
		panel3.setVisible(true);
		return panel3;
	}
	
	public  ArrayList<OrderClass> getOrders()
	{
		return orders;
	}	
}