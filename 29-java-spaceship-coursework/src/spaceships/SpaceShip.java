package spaceships;


import java.awt.Color;
import javax.swing.ImageIcon;
import java.awt.Rectangle;

import main.MainClass;
import spaceships_laserguns.Lasergun;


abstract public class SpaceShip implements Navigation
{
	protected String SpaceShipName;
	protected int speed_x;
	protected int speed_y;	
	protected int Xcord;
	protected int Ycord;
	protected ImageIcon SpaceShipImageIcon;
	public Lasergun gun;
	//public static Rectangle rec;
	
	
	SpaceShip(Color clr)
	{	
		gun=new Lasergun(clr);
	}
	
	
	public int moveUP()
	{
		 Ycord -= speed_y;
		 if (Ycord <= 0)  
		 {
			 Ycord = MainClass.cosmosHeight;
		 }
		 
		 
		 return Ycord;
	 }
		 

	  
	 public int moveDOWN()
	 {
		 Ycord += speed_y;
		// if (Ycord  >= MainClass.cosmosHeight - MainClass.spaceShipHeight)
		// {
			// Ycord = MainClass.cosmosHeight - MainClass.spaceShipHeight;
		 //}
		 
		 
		 if (Ycord >= MainClass.cosmosHeight)
		 {
			 Ycord = 0;
		 }
		 return Ycord;
	 }
	 
	 
	  public int moveRIGHT()
	  {
		 Xcord += speed_x;
		 //if (Xcord > MainClass.cosmosWidth - MainClass.spaceShipWidth)
		 //{
			 //Xcord = MainClass.cosmosWidth - MainClass.spaceShipWidth;
		 if (Xcord >= MainClass.cosmosWidth - MainClass.spaceShipWidth)
		 {
			 Xcord = 0;
		 }
		 
		 if (Xcord < 0)
		 {
			 Xcord = MainClass.cosmosWidth - MainClass.spaceShipWidth;
		 }
		// }
		 
		 return Xcord;
	  }
	 
	 
	  public int moveLEFT()
	  {
		  Xcord -= speed_x;
		  //if (Xcord <= 0)
		  //{
			//  Xcord = 0;
		  //}
		  
		  if (Xcord >= MainClass.cosmosWidth - MainClass.spaceShipWidth)
			 {
				 Xcord = 0;
			 }
			 
			 if (Xcord < 0)
			 {
				 Xcord = MainClass.cosmosWidth - MainClass.spaceShipWidth;
			 }
		  
		  return Xcord;
	  }
	  
	  public int moveMOUSEx (int xcord)
	  {
		  Xcord = xcord;
		  return Xcord;
		  
	  }
	
	  public int moveMOUSEy (int ycord)
	  {
		  Ycord = ycord;
		  return Ycord;
		  
	  }
	  
	
	
	public void printCords()
	{
		System.out.println(" x = " + Xcord + " y = " + Ycord);
	}

	public ImageIcon getIcon()
	{
		return SpaceShipImageIcon;
	}

	public int getX()
	{
		return Xcord;
	}

	public int getY()
	{
		return Ycord;
	}
	
	public Rectangle getBoundingRectangle() {
		return new Rectangle(MainClass.cosmosHeight, MainClass.cosmosWidth, Xcord, Ycord);
	}
}
	
	



