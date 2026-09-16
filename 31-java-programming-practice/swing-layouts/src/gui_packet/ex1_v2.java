package gui_packet;


import java.awt.FlowLayout;
import javax.swing.JButton;
import javax.swing.JFrame;

public class ex1_v2 extends JFrame{	
	private static final long serialVersionUID = 1L;
	ex1_v2(){
		this.setSize(100, 100);	
		this.setTitle("[ECE_Υ325] Layout Managers");
		this.setDefaultCloseOperation(EXIT_ON_CLOSE);
		this.setLocationRelativeTo(null); 		
		this.setFocusable(true);
		
		this.setLayout(new FlowLayout());
		
		this.add(new JButton("Ok"));
		this.add(new JButton("Cancel"));
		
		
		setResizable(true);
		this.setVisible(true);
	}
	
	public static void main(String[] args) {
		 	ex1_v2 x=new ex1_v2();
    }
}