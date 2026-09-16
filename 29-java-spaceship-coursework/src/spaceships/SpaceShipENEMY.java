package spaceships;

import java.awt.Color;
import java.awt.Image;
import java.awt.Rectangle;
import java.util.Random;

import javax.imageio.ImageIO;
import javax.swing.ImageIcon;

import main.MainClass;

import java.awt.Rectangle;

public class SpaceShipENEMY extends SpaceShip
{
	static Random random  = new Random();
	public static Image img;
	static
    {
		try
		{
			SpaceShipENEMY.img=ImageIO.read(MainClass.class.getResource("../images/ENEMY.png"));
			SpaceShipENEMY.img =SpaceShipENEMY.img.getScaledInstance(MainClass.spaceShipWidth, 
					MainClass.spaceShipHeight, 0);
		    
		}
		catch (Exception ex) {System.out.println(ex);}
    }
	public SpaceShipENEMY()
	{
		super(Color.MAGENTA);
		SpaceShipName="ENEMY";
		speed_x=40;
		speed_y=40;
		Xcord=MainClass.cosmosWidth-MainClass.spaceShipWidth;
		Ycord=0;
		//rec = new Rectangle(MainClass.cosmosHeight, MainClass.cosmosWidth, Xcord, Ycord);
		super.SpaceShipImageIcon=new ImageIcon(SpaceShipENEMY.img);
	}
	
	
	
    public void huntUserSpaceShip(SpaceShip userSpaceShip)
    {
    	int mv = random.nextInt(10);
    	if(mv == 0)this.gun.fire(this.getX(),this.getY()+100);
    	if(userSpaceShip.Xcord>this.Xcord)this.Xcord=this.moveRIGHT();
    	else this.Xcord=this.moveLEFT();
    	
    	int res = random.nextInt(4);	
    	if (res == 2) this.moveLEFT();
    	if (res == 3) this.moveRIGHT();
	} 	
}
