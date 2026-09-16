package gui;


import java.awt.Color;
import java.awt.Graphics;
import java.awt.MouseInfo;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.MouseEvent;
import java.util.Timer;
import java.util.TimerTask;
import java.util.LinkedList;
import javax.swing.JLabel;
import javax.swing.ImageIcon;
import java.awt.event.MouseListener;
import java.awt.Point;
import java.awt.Image;
import java.awt.Toolkit;
import java.awt.*;
import java.awt.image.BufferedImage;

import javax.imageio.ImageIO;
import javax.swing.*;
//
import javax.swing.JPanel;


import main.MainClass;
import spaceships.*;

public class GamePlayScreen extends JPanel implements KeyListener, MouseListener{
	private static final long serialVersionUID = 1L;
	public int lives = 15;
	private SpaceShip userSpaceShip;
	private SpaceShipENEMY enemySpaceShip;
	int c;
	public int xcord;
	public int ycord;
	public static Image background;
	public static Image newImage;
	
	

	GamePlayScreen()
	{   	
     	addKeyListener(this);
     	addMouseListener(this);
    	this.setVisible(true);
    	 background = Toolkit.getDefaultToolkit().createImage("Resources\\images\\nebula3.jpg\\");
    	newImage = background.getScaledInstance( (int)MainClass.screenSize.getWidth(), (int)MainClass.screenSize.getHeight(), Image.SCALE_DEFAULT);
    	this.setBackground(Color.black);
    	createDaemon();
    }
	
	
	private void createDaemon()
	{
		Timer timer = new Timer();
        TimerTask task = new monitorDeamonGame();  
        timer.schedule(task, 100, 100);
    }
        class monitorDeamonGame extends TimerTask
        {
	      public void run(){repaint();} 
        }
        
        
	 @Override
	 public void paintComponent (Graphics g)
	 {   	
	        super.paintComponent(g);
	        Graphics2D g2D = (Graphics2D) g; // μήπως και γίνει κάτι
	        g.drawImage(newImage, 0, 0, null);
	        enemySpaceShip.huntUserSpaceShip(userSpaceShip);
	        userSpaceShip.getIcon().paintIcon(this, g2D, userSpaceShip.getX(), userSpaceShip.getY());
	        enemySpaceShip.getIcon().paintIcon(this, g2D, enemySpaceShip.getX(), enemySpaceShip.getY());
	        
	        showLaserShootings(g2D);
	        //icon.paintIcon(this, g2D, 0, 0);
	        //g2D.drawImage(background, 0, 0, this);
	 }
	 
	private void showLaserShootings(Graphics g)
	{
		userSpaceShip.gun.laserShootersLinkedList.forEach((tmp) -> {
            g.setColor(userSpaceShip.gun.lasercolor);
            g.drawLine(tmp.x, tmp.y, tmp.x, tmp.y-15);
            tmp.y=tmp.y-15; // για κάθε σημείο ζωγραφίζω μία γραμμή και τη μετακινώ προς τα πάνω
       });
		enemySpaceShip.gun.laserShootersLinkedList.forEach((tmp) -> {
            g.setColor(enemySpaceShip.gun.lasercolor);
            g.drawLine(tmp.x, tmp.y, tmp.x, tmp.y+15);
            if (tmp.y > MainClass.screenSize.getHeight() && tmp.x > MainClass.screenSize.getWidth() )
            {
            	enemySpaceShip.gun.laserShootersLinkedList.remove(tmp); // not to cause memory leakage
            }
            else
            {
            	tmp.y=tmp.y+15;
            }
            if(userSpaceShip.getBoundingRectangle().intersectsLine(tmp.x, tmp.y, tmp.x, tmp.y + 15)){
            	System.out.println("Colision");
            	lives-=1;
            	System.out.println(lives);
            	if(lives < 0) 
            	{
            		System.exit(0);  
            	}
            }
            
          
			
			  //check_colisions(tmp.x, tmp.y);
					  
       });
	}
	 
	@Override
	public void keyPressed (KeyEvent e)
	{  
		if (e.getKeyCode() == KeyEvent.VK_UP) userSpaceShip.moveUP();
		if (e.getKeyCode() == KeyEvent.VK_DOWN) userSpaceShip.moveDOWN();
		if (e.getKeyCode() == KeyEvent.VK_LEFT) userSpaceShip.moveLEFT();
		if (e.getKeyCode() == KeyEvent.VK_RIGHT) userSpaceShip.moveRIGHT();
		if (e.getKeyCode() == KeyEvent.VK_SPACE) userSpaceShip.gun.fire(userSpaceShip.getX(),userSpaceShip.getY());
		if (e.getKeyCode() == KeyEvent.VK_B)SpaceFrame.cardLayout.next(SpaceFrame.spaceFramePanel);

	    this.repaint();
    }    
	
	@Override
	public void keyReleased (KeyEvent e) {}    
	
	@Override
	public void keyTyped (KeyEvent e){}
	
	void intGame(SpaceShip usel)
	{
		userSpaceShip=usel;
		enemySpaceShip= new SpaceShipENEMY();
	}
	
	//private void check_colisions(int x, int y)
	//{
		// if (y == (MainClass.cosmosHeight - MainClass.spaceShipHeight) && (x >= userSpaceShip.getX() && x <= userSpaceShip.getX() + MainClass.spaceShipWidth));
		  //{
			 // lives--;
			  //System.out.println("oof");
			  
		  //} // lol περνάει το y = 5 GG ._.
		  
	//}
	@Override
	public void mouseClicked(MouseEvent e)
	{
		//also this does not work
		
		Point mouselocation = MouseInfo.getPointerInfo().getLocation();
		int mouse_x = (int)mouselocation.getX();
		int mouse_y = (int) mouselocation.getY();
		userSpaceShip.moveMOUSEx(mouse_x);
		userSpaceShip.moveMOUSEy(mouse_y);
		this.repaint();
		
		
		
		
		
	}
	@Override
	public void mousePressed(MouseEvent e)
	{
		// TODO Auto-generated method stub
		
	}
	@Override
	public void mouseReleased(MouseEvent e)
	{
		// TODO Auto-generated method stub
		
	}
	@Override
	public void mouseEntered(MouseEvent e)
	{
		// TODO Auto-generated method stub
		
	}
	@Override
	public void mouseExited(MouseEvent e)
	{
		// TODO Auto-generated method stub
		
	}
	
	
}