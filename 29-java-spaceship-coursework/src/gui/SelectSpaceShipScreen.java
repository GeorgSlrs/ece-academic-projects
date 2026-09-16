package gui;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Cursor;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridLayout;
import java.awt.Panel;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.border.Border;
import javax.swing.border.LineBorder;

import spaceships.SpaceShipALPHA;
import spaceships.SpaceShipBETA;
import spaceships.SpaceShipDELTA;
import spaceships.SpaceShipGAMA;
import spaceships.SpaceShipZERO;

//public class SelectSpaceShipScreen extends Panel implements ActionListener{
	
public class SelectSpaceShipScreen extends JPanel
{
	
	/*public void actionPerformed(ActionEvent ev)
	 * {
		   JButton o = (JButton)ev.getSource();
		   String name = o.getName();
		   if(name.equalsIgnoreCase("SZERO")) System.out.println("SPACESHIPZERO CLICKED");
		
	}*/
	
	private static final long serialVersionUID = 1L;
	
	
	SelectSpaceShipScreen()
	{
		this.setLayout(new BorderLayout());
		this.add(createNorthPanel(), BorderLayout.NORTH);
    	this.add(createCenterPanel(), BorderLayout.CENTER);
		this.add(createSouthPanel(), BorderLayout.SOUTH);
		this.setBackground(Color.BLACK);
    }
	
	private JPanel createNorthPanel()
    {
        JPanel panel = new JPanel();
        //panel.setPreferredSize(new Dimension(100, 100));
        JLabel label = new JLabel("Oof "); 
        //label.setFont(new Font("Arcade Classic", Font.PLAIN, 25));
        label.setFont(new Font("Arial", Font.BOLD, 25));
        label.setForeground(Color.green);
        //label.setForeground(Color.WHITE);
        panel.setBackground(Color.BLACK);
        panel.add(label);
        return panel;
    }
	
	private JPanel createCenterPanel()
	{
		
		//btnspaceShipZero.addActionListener(this);
	
		/*btnspaceShipZero.addActionListener( new ActionListener()
		{
		    @Override
		    public void actionPerformed(ActionEvent e)
		    {
		        System.out.println("User Choose Spaceship ZERO");
		    }
		});*/
		JButton btnspaceShipZero=new JButton(); 
		JButton btnspaceShipAlpha=new JButton();  
		JButton btnspaceShipBeta=new JButton();  
		JButton btnspaceShipGama=new JButton();  
		JButton btnspaceShipDelta=new JButton(); 
		btnspaceShipZero.addActionListener(new SpaceShipSelectionBtnHandler("ZERO"));
		btnspaceShipAlpha.addActionListener(new SpaceShipSelectionBtnHandler("ALPHA"));
		btnspaceShipBeta.addActionListener(new SpaceShipSelectionBtnHandler("BETA"));
		btnspaceShipGama.addActionListener(new SpaceShipSelectionBtnHandler("GAMA"));
		btnspaceShipDelta.addActionListener(new SpaceShipSelectionBtnHandler("DELTA"));
		
		btnspaceShipZero.setIcon(new ImageIcon(SpaceShipZERO.img));
		btnspaceShipAlpha.setIcon(new ImageIcon(SpaceShipALPHA.img));
		btnspaceShipBeta.setIcon(new ImageIcon(SpaceShipBETA.img));
		btnspaceShipGama.setIcon(new ImageIcon(SpaceShipGAMA.img));
		btnspaceShipDelta.setIcon(new ImageIcon(SpaceShipDELTA.img));
		makeBtnsTransparent(btnspaceShipZero);
		makeBtnsTransparent(btnspaceShipAlpha);
		makeBtnsTransparent(btnspaceShipBeta);
		makeBtnsTransparent(btnspaceShipGama);
		makeBtnsTransparent(btnspaceShipDelta);
		
		
		
	
	
		JPanel panel = new JPanel();
        panel.setLayout(new GridLayout());
        
        Border border1 = new LineBorder(Color.DARK_GRAY, 4, true);
		panel.setBorder(border1);
        panel.setBackground(Color.BLACK);
        panel.add(btnspaceShipZero);  
        panel.add(btnspaceShipAlpha);  
        panel.add(btnspaceShipBeta);
        panel.add(btnspaceShipGama);
        panel.add(btnspaceShipDelta);
        return panel;
		
	}
	
	private JPanel createSouthPanel()
	{
		JPanel panelSouth = new JPanel();
        panelSouth.setPreferredSize(new Dimension(100, 200));
        panelSouth.setBackground(Color.BLACK);
        return panelSouth;
		
	}

	private void makeBtnsTransparent(JButton btn)
	{
		btn.setBackground(Color.BLACK);
		btn.setOpaque(false);
		btn.setContentAreaFilled(false);
		//btn.setBorderPainted(false);
		btn.setFocusPainted( false );
		Border border2 = new LineBorder(Color.RED, 4, true);
		btn.setBorder(border2);
		btn.setCursor(new Cursor(Cursor.HAND_CURSOR)); // This one line changes the cursor.
	}
	
	 
	class SpaceShipSelectionBtnHandler implements ActionListener
	{
			String name;
			public SpaceShipSelectionBtnHandler(String x) {
				name = x; 
			}
			public void actionPerformed(ActionEvent ev){
				SpaceFrame.cardLayout.next(SpaceFrame.spaceFramePanel);
				SpaceFrame.gamePlayScreen.setFocusable(true);//in order to catch the keyevents
				SpaceFrame.gamePlayScreen.requestFocus(); // γιατί το βάζουμε αυτό;
				
				if(name.equalsIgnoreCase("ZERO"))SpaceFrame.gamePlayScreen.intGame(new SpaceShipZERO());
				if(name.equalsIgnoreCase("ALPHA")) SpaceFrame.gamePlayScreen.intGame(new SpaceShipALPHA());
				if(name.equalsIgnoreCase("BETA"))SpaceFrame.gamePlayScreen.intGame(new SpaceShipBETA());
				if(name.equalsIgnoreCase("GAMA"))SpaceFrame.gamePlayScreen.intGame(new SpaceShipGAMA());
				if(name.equalsIgnoreCase("DELTA"))SpaceFrame.gamePlayScreen.intGame(new SpaceShipDELTA());
				
				
				
			}	
		}
}
