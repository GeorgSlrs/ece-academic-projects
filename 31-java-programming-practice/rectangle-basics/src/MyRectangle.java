class MyRectangle {
	// Data members
	double width = 1, height = 1;
	
	// Constructor
	public MyRectangle(double newWidth, double newHeight) {
		width = newWidth;
		height = newHeight;
				
	}
	
	public double getArea() {
		return width * height;
	}
	
	public double getPerimeter() {
		return 2 * (width + height);
	}
	
}
