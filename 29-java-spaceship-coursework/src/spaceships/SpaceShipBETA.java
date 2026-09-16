package spaceships;

import java.awt.Color;
import java.awt.Image;
import java.awt.Rectangle;

import javax.imageio.ImageIO;
import javax.swing.ImageIcon;
import java.awt.Rectangle;
import main.MainClass;

public class SpaceShipBETA extends SpaceShip
{
	
	public static Image img;
	static
    {
		try
		{
			SpaceShipBETA.img=ImageIO.read(MainClass.class.getResource("../images/BETA.png"));
		}
		catch (Exception ex) {System.out.println(ex);}
    }
	public SpaceShipBETA()
	{
		super(Color.BLUE);
		SpaceShipName="BETA";
		speed_x=20;
		speed_y=20;
		Xcord=0;
		Ycord=MainClass.cosmosHeight-MainClass.spaceShipHeight;
		//rec = new Rectangle(MainClass.cosmosHeight, MainClass.cosmosWidth, Xcord, Ycord);
		super.SpaceShipImageIcon=new ImageIcon(SpaceShipBETA.img);
	}

	
	
	
}
