package spaceships;

import java.awt.Color;

import java.awt.Image;
import java.awt.Rectangle;

import javax.imageio.ImageIO;
import javax.swing.ImageIcon;

import main.MainClass;
import java.awt.Rectangle;


public class SpaceShipDELTA extends SpaceShip
{
	
	public static Image img;
	static
    {
		try
		{
			SpaceShipDELTA.img=ImageIO.read(MainClass.class.getResource("../images/DELTA.png"));
		}
		catch (Exception ex) {System.out.println(ex);}
    }
	public SpaceShipDELTA()
	{
		super(Color.GREEN);
		SpaceShipName="DELTA";
		speed_x = 40;
		speed_y = 40;
		Xcord = 0;
		Ycord =MainClass.cosmosHeight-MainClass.spaceShipHeight;
		//rec = new Rectangle(MainClass.cosmosHeight, MainClass.cosmosWidth, Xcord, Ycord);
		super.SpaceShipImageIcon=new ImageIcon(SpaceShipDELTA.img);
	}
	
	

	
	
}
