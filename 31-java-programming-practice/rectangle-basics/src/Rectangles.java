
public class Rectangles{
	static public void main(String [] args) {
		MyRectangle objRecA = new MyRectangle(2,2);
		System.out.println("The area of a rectangle with width " + objRecA.getArea());
		System.out.println("The perimeter of a rectangle is " + objRecA.getPerimeter());
		MyRectangle objRecB = new MyRectangle(3.0, 35.0);
		System.out.println("The area of a rectangle with width " + objRecB.getArea());
		System.out.println("The perimeter of a rectangle is " + objRecB.getPerimeter());

	}
}
	
