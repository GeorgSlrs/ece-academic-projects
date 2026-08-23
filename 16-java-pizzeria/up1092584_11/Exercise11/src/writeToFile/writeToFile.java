package writeToFile;


import java.util.Collections;
import java.io.FileWriter;
import java.io.IOException;
import threads.*;

import Pizzeria.*;

//max and min waiting times ->get the min and max of the waitingTimes Array
//revenue
//avg waiting time

//yes the code is very ugly

public class writeToFile
{
	
	public writeToFile()
	{
		try {
		      FileWriter myWriter = new FileWriter("filename.txt");
		      myWriter.write("FIFO");
		      myWriter = writeMaxMinWaitingTimes(threadFIFO.returnInstance(), myWriter);
		      myWriter = avgWaitingTime(threadFIFO.returnInstance(),  myWriter);
		      myWriter = writeRevenue(threadFIFO.returnInstance(), myWriter);
		      myWriter.write("==================================================");
		      myWriter.write("\n\n");
		      myWriter.write("Profit");
		      myWriter = writeMaxMinWaitingTimes(threadProfit.returnInstance(), myWriter);
		      myWriter = avgWaitingTime(threadProfit.returnInstance(),  myWriter);
		      myWriter = writeRevenue(threadProfit.returnInstance(), myWriter);
		      myWriter.write("\n\n");
		      myWriter.write("==================================================");
		      myWriter.write("Random");
		      myWriter = writeMaxMinWaitingTimes(threadRandom.returnInstance(), myWriter);
		      myWriter = avgWaitingTime(threadRandom.returnInstance(),  myWriter);
		      myWriter = writeRevenue(threadRandom.returnInstance(), myWriter);
		      myWriter.write("\n\n");
		      myWriter.write("==================================================");
		      
		     // myWriter.close();
		      //System.out.println("Successfully wrote to the file.");
		    
			} 
		catch (IOException e) 
		{
		      System.out.println("An error occurred while writing data into the file.");
		      e.printStackTrace();		      
		}
		
	}
	
	
	
	// στις παρακάτω μεθόδους γίνεται αυτόματο  upcasting. Πχ έχουμε ένα αντικείμενο PizzaFIFO
	// γίνεται αυτόματα upcast σε Pizzeria
	
	public FileWriter writeMaxMinWaitingTimes(Pizzeria obj, FileWriter writer)
	{
		
		
		try
		{
			writer.write(Collections.min(obj.waitingTimes.values()));
			writer.write(Collections.max(obj.waitingTimes.values()));
			
		} catch (IOException e)
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
																			
		return writer;
	}
	
	
	public FileWriter avgWaitingTime(Pizzeria obj, FileWriter writer)
	{
		try
		{
			writer.write(obj.getAverage(obj.waitingTimes));
		} catch (IOException e)
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return writer;
	}
	
	
	public FileWriter writeRevenue(Pizzeria obj, FileWriter writer)
	{
		try
		{
			writer.write(obj.revenue);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return writer;
	}
		
}