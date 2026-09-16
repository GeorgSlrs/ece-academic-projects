package spaceships;
import java.awt.Color;
import java.awt.Image;

import javax.imageio.ImageIO;
import javax.swing.ImageIcon;
import java.awt.Rectangle;

import main.MainClass;

public class SpaceShipALPHA extends SpaceShip
{
	
	public static Image img;
	static
    {
		try
		{
			SpaceShipALPHA.img=ImageIO.read(MainClass.class.getResource("../images/ALPHA.png"));
		}
		catch (Exception ex) {System.out.println(ex);}
    }
	
	public SpaceShipALPHA()
	{
		super(Color.cyan);
		SpaceShipName="ALPHA";
		speed_x=10;
		speed_y=10;
		Xcord=0;
		Ycord =MainClass.cosmosHeight-MainClass.spaceShipHeight;
		//rec = new Rectangle(MainClass.cosmosHeight, MainClass.cosmosWidth, Xcord, Ycord);
		super.SpaceShipImageIcon=new ImageIcon(SpaceShipALPHA.img);
	}
	
	
	
	
}
