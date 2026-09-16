package gui;


import java.awt.CardLayout;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import java.awt.Graphics;
import java.awt.Image;
import java.awt.Toolkit;
import java.io.IOException;
import javax.imageio.ImageIO;
import javax.swing.ImageIcon;
import java.io.File;
import java.awt.FlowLayout;


import sounds.GameAudioPlayer;


public class SpaceFrame extends JFrame{
	private static final long serialVersionUID = 1L;
	static int width;
	static int height;
	static SelectSpaceShipScreen selectSpaceShipScreen=new SelectSpaceShipScreen();
	static GamePlayScreen gamePlayScreen=new GamePlayScreen();;
	static CardLayout cardLayout=new CardLayout();
	static JPanel spaceFramePanel=new JPanel();
	//public JLabel background;
	public static GameAudioPlayer gameAudioPlayer=new GameAudioPlayer();
	//private ImageIcon spaceicon;
	//private JLabel space_label;
	
	public SpaceFrame(int width, int height)
	{
		SpaceFrame.width=width;
		SpaceFrame.height=height;
		this.setSize(width, height);
		//spaceicon = new ImageIcon(this.getClass().getResource("Resources\\images\\nebula.jpg"));
		//space_label  = new JLabel(spaceicon);
		//space_label.setSize(600, 800);
		//this.add(space_label);
		//JLabel background=new JLabel(new ImageIcon("Resources//images//nebula.jpg"));
		//background.setSize(600, 800);
		//background.setVisible(true);
		//this.add(background);
		//background.setLayout(new FlowLayout());
		
		// γιατί δε δουλεύει αυτή η προσέγγιση...
		 //ImageIcon img = new ImageIcon("nebula.jpg");

	       // background = new JLabel("",img,JLabel.CENTER);
	       // background.setBounds(0,0,600,800);
	        //this.add(background);
		//Image img = Toolkit.getDefaultToolkit().getImage("..]\nebula.jpg");
		//try {
			  //this.setContentPane(
			    //new JLabel(new ImageIcon(ImageIO.read(new File("Resources\\images\\nebula.jpg")))));
			//} catch (IOException e) {System.out.println(e);};
		// μέχρι στιγμής 6 προσπάθειες να βάλω backround εικόνα..
		// καμία δε λειτουργεί
		//splendid
		// θα διαβάσει κανείς τα σχόλια αυτά  άραγε;
		// oof στην έβδομη φορά βγήκε
		
		this.setTitle("Spent days on this and does not even work properly. Nice");
		this.setDefaultCloseOperation(EXIT_ON_CLOSE);	
		this.setLocationRelativeTo(null); 		
		this.setFocusable(true);
		setupMasterPanel();
		setResizable(false);
		this.setVisible(true); 		
	}
	
	void setupMasterPanel()
	{
		spaceFramePanel.setLayout(cardLayout);
		spaceFramePanel.add(selectSpaceShipScreen);
		spaceFramePanel.add(gamePlayScreen);
		this.add(spaceFramePanel);
		
	}
	
	//
}
