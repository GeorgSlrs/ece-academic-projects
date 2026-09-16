package waterProd;

public class WaterProduction {
    private static final int NUM_WATER_MOLECULES = 100;

    private static int numHydrogen = 0;
    private static int numOxygen = 0;

    public static void main(String[] args) throws InterruptedException {
        Thread hydrogenProducer = new Thread(() -> {
            while (true) {
                synchronized (WaterProduction.class) {
                    numHydrogen++;
                    WaterProduction.class.notifyAll();
                }
            }
        });

        Thread oxygenProducer = new Thread(() -> {
            while (true) {
                synchronized (WaterProduction.class) {
                    numOxygen++;
                    WaterProduction.class.notifyAll();
                }
            }
        });

        Thread waterProducer = new Thread(() -> {
            while (true) {
                synchronized (WaterProduction.class) {
                    while (numHydrogen < 2 || numOxygen < 1) {
                        try {
                            WaterProduction.class.wait();
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                    }

                    numHydrogen -= 2;
                    numOxygen--;
                   // NUM_WATER_MOLECULES--;

                    if (NUM_WATER_MOLECULES == 0) {
                        // Stop the program
                        System.exit(0);
                    }
                }
            }
        });

        hydrogenProducer.start();
        oxygenProducer.start();
        waterProducer.start();
    }
}