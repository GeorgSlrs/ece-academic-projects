package spaceships;
import java.awt.Color;
import java.awt.Image;
import java.awt.Rectangle;

import javax.imageio.ImageIO;
import javax.swing.ImageIcon;

import main.MainClass;

import java.awt.Rectangle;

public class SpaceShipZERO extends SpaceShip
{
	
	public static Image img;
	static
    {
		try{
			SpaceShipZERO.img=ImageIO.read(MainClass.class.getResource("../images/ZERO.png"));
		}
		catch (Exception ex) {System.out.println(ex);}
    }
	
	public SpaceShipZERO()
	{
		super(Color.YELLOW);
		SpaceShipName="ZERO";
		speed_x=5;
		speed_y=5;
		Xcord=0;
		Ycord=(MainClass.cosmosHeight-MainClass.spaceShipHeight);
		//rec = new Rectangle(MainClass.cosmosHeight, MainClass.cosmosWidth, Xcord, Ycord);		
		super.SpaceShipImageIcon=new ImageIcon(SpaceShipZERO.img);
	}
	
}
