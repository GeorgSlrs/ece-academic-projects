package packet1;

import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
public class Prac1
{
	public static void main(String[] args) {
		ExecutorService exec = Executors.newCachedThreadPool();
		
		tasksClass task_a = new tasksClass();
		tasksClass task_b = new tasksClass();
		
		exec.execute(task_a);
		exec.execute(task_b);
		
		exec.shutdown();
		
		System.out.println("Main has ended.");
		
	}

}
