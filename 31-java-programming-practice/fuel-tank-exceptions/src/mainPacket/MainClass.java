package mainPacket;
import java.util.Scanner;

import tankFuel.*;

public class MainClass{
	public static void main(String[] args) {
		Scanner in = new Scanner (System.in);
		System.out.println("Enter fuel rate: (0.1 or 0.2 supported) ");
	    double fuel_rate = in.nextDouble();
	    System.out.println("Enter tank's capacity: ");
	    double tank_capacity = in.nextDouble();
	    TankFuel tank = new TankFuel(tank_capacity);
		
		boolean stop_filling = false;
		while(!stop_filling)
		{
			try {
				tank.fuelTank(fuel_rate);
			}
			
			catch (InvalidFuelRate exc) {;
				stop_filling = true;
				System.out.println(exc.getMessage());
			}
			
			catch (TankAlreadyFull exc2) {
				stop_filling = true;
				System.out.println(exc2.getMessage());
			}
			
			catch (NegativeCapacity exc3) {
				stop_filling = true;
				System.out.println(exc3.getMessage());
			}
			
			catch (UnableToFillTank exc4) {
				stop_filling = true;
				System.out.println(exc4.getMessage());
			}
		}
		in.close();
	}
}
