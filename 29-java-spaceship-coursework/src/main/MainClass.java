package main;


import gui.SpaceFrame;
import java.awt.Toolkit;
import java.awt.Dimension;
// note to self : next version: add a proper exit window not just exit the game

// ideas 
// healthbar future version
// full-screen
// background image
// αν πέσει σε border να ξαναεμφανίζεται από την επόμενη πλευρά
// κίνηση με ποντίκι
// αλλάζω μουσική
// συνθήκη τερματισμού - πότε έχω σύγκρουση


public class MainClass 
{
	public static Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
	public static int cosmosWidth = (int)screenSize.getWidth();
    public static int cosmosHeight = (int)screenSize.getHeight();
    public static int spaceShipWidth=100;
    public static int spaceShipHeight=100;
    public static SpaceFrame myShootingGame;
    
    
    public static void main(String[] args)
    {
    	
    	myShootingGame=new SpaceFrame(cosmosWidth,cosmosHeight);
    }
}
