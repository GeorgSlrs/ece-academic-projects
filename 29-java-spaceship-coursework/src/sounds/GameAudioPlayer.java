package sounds;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.Clip;
import javax.sound.sampled.FloatControl;

import main.MainClass;
public class GameAudioPlayer {
	private  AudioInputStream audioInputStream;
	Clip clip;
	public GameAudioPlayer(){
			loadSpaceAmbient();
   }
	void loadSpaceAmbient() {
		try{
		audioInputStream = 
			    AudioSystem.getAudioInputStream(MainClass.class.getResource("../audio/track3.wav"));
				clip = AudioSystem.getClip();
			    clip.open(audioInputStream);
	      	    clip.loop(Clip.LOOP_CONTINUOUSLY);
	      	
	   
	         	FloatControl gainControl = 
	      		    (FloatControl) clip.getControl(FloatControl.Type.MASTER_GAIN);
	      		gainControl.setValue(-15.0f); // Reduce volume by 15 decibels.	
	      	
	      	
	      	clip.start();
		}
		catch (Exception ex) {System.out.println(ex);}
		
	}	
}
