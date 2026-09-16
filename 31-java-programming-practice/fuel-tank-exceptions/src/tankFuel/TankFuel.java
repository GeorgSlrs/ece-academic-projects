package tankFuel;

public class TankFuel {
	private final double gasolineTankCapacity;
	private double tankFuel = 0.0;
	
	public TankFuel(double gasolineTankCapacity){
		this.gasolineTankCapacity = gasolineTankCapacity;
	}
	
	public double getTankFuel(){
		return tankFuel;
	}
	
	public double getTankCapacity() {
		return gasolineTankCapacity;
	}
	
	public void fuelTank(double fill_rate) throws InvalidFuelRate, TankAlreadyFull, NegativeCapacity, UnableToFillTank {
		if (tankFuel == gasolineTankCapacity) throw new TankAlreadyFull ("The tank is already full. You cannot add more fuel.");
		
		if (fill_rate != 0.1 && fill_rate != 0.2)
			throw new InvalidFuelRate("Fill rate of the tank is not supported.");
		if (gasolineTankCapacity <= 0) throw new NegativeCapacity("Cannot create a tank with this capacity");
		if (tankFuel + fill_rate > gasolineTankCapacity) throw new UnableToFillTank("Unable to fill the tank 100%");
		else {
			System.out.println("Fuel tank before fill: " + tankFuel);
			tankFuel += fill_rate;
			System.out.println("Tank after fill: " + tankFuel);
			tankFuel = (double)Math.round(tankFuel * 10) / 10; // Xωρίς αυτή τη γραμμή τα νούμερα ξεφεύγουν αρκετά.Δε γνωρίζω γιατί.
			// gasolineTankCapacity += fill_rate; δε μπορώ να την αλλάξω.
		}
		
		
		
	}
}		
	
	


