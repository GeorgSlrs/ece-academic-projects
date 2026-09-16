package gui_packet;


import java.awt.FlowLayout;
import javax.swing.JButton;
import javax.swing.JFrame;

public class Mainclass2 extends JFrame{	
	private static final long serialVersionUID = 1L;
	Mainclass2(){
		this.setSize(100, 100);	
		this.setTitle("[ECE_Υ325] Layout Managers");
		this.setDefaultCloseOperation(EXIT_ON_CLOSE);
		this.setLocationRelativeTo(null); 		
		this.setFocusable(true);
		
		this.setLayout(new FlowLayout());
		
		this.add(new JButton("A"));
		this.add(new JButton("B"));
		
		this.add(new JButton("C"));
		this.add(new JButton("D"));
		this.add(new JButton("E"));
		this.add(new JButton("F"));
		
		setResizable(true);
		this.setVisible(true);
	}
	
	public static void main(String[] args) {
		 	Mainclass2 x=new Mainclass2();
    }
}