public class Rectangle {
	private float downl_x=0;
	private float downl_y=0;
	private float width = 0;
	private float height = 0;
	private static int number_of_recs = 0;
	
	public Rectangle(float new_downl_x, float new_down_ly, float new_width, float new_height){
		downl_x = new_downl_x;
		downl_y = new_down_ly;
		width = new_width;
		height = new_height;
		number_of_recs++;
	}
	// Παίρνουμε το σχήμα του pdf- κάτω άκρο (0,0)
	// Άμα το σημείο είναι δεξιά αλλά χωρίς να ξεπεράσει
	// το width + 0 και το height + 0 , τότε True
	// Αμα το x_cor < downl_x βρίσκεται αριστερά της κάτω αριστερής γωνίας του ορθογωνίου
	// Ομοίως για y
	// Θεωρούμε ορθογώνιο με κάτω αριστερά συντεταγμένη διαφορη του (0,0)
	// Θεωρούμε καινούργιο σύστημα αξόνων με βάση την κάτω αριστερά γωνία του ορθογωνίου
	// Με μετατόπιση αξόνων προκύπτει ότι θα πρέπει και x_cor <= width + downl_x
	// Oμοίως για y_cor
	public boolean contains(float x_cor, float y_cor) {
		boolean contains_rec = false;
		if((x_cor >= downl_x) && (x_cor <= width + downl_x))
			if((y_cor >= downl_y) && (y_cor <= height + downl_y))
				contains_rec = true;
		return contains_rec;
	}
	
	static public void PrintNumber_Recs() {
		System.out.println("Number of Rectangles: " + number_of_recs);
	}
}
