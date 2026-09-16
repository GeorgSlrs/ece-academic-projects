package packet1;
import java.util.Random;
public class tasksClass implements Runnable
{
	
	public static Random generator = new Random();
	@Override
	public void run() {
		// TODO Auto-generated method stub
		int i, delay;
		String name;
		
		name = Thread.currentThread().getName();
		
		for (i = 0; i < 10; i++) {
			try
			{
				delay = generator.nextInt(2000);
				Thread.sleep(delay);
				System.out.printf("%s:\t%d\n",name,i);
			}
			
			catch (InterruptedException exception)
			{
				
			}
			
		}
	}

}
