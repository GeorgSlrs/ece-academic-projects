package spaceships;

import java.awt.Color;
import java.awt.Image;
import java.awt.Rectangle;

import javax.imageio.ImageIO;
import javax.swing.ImageIcon;

import main.MainClass;

import java.awt.Rectangle;

public class SpaceShipGAMA extends SpaceShip
{
	
	public static Image img;
	static
    {
		try
		{
			SpaceShipGAMA.img=ImageIO.read(MainClass.class.getResource("../images/GAMA.png"));
		}
		catch (Exception ex) {System.out.println(ex);}
    }
	public SpaceShipGAMA()
	{
		super(Color.RED);
		SpaceShipName="GAMA";
		speed_x=30;
		speed_y=30;
		Xcord=0;
		speed_y=MainClass.cosmosHeight-MainClass.spaceShipHeight;
		//rec = new Rectangle(MainClass.cosmosHeight, MainClass.cosmosWidth, Xcord, Ycord);
		super.SpaceShipImageIcon=new ImageIcon(SpaceShipGAMA.img);
	}

	
	
	
}
