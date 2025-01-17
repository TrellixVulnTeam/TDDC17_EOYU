public class StateAndReward {

	private static double maxAngle = Math.PI;
	private static int angleStates = 10;
	private static int vxStates = 7;
	private static int maxVx = 25;
	private static int vyStates = 8;
	private static int maxVy = 30;
	
	/* State discretization function for the angle controller */
	public static String getStateAngle(double angle, double vx, double vy) {

		/* TODO: IMPLEMENT THIS FUNCTION */
		
		return String.valueOf(discretize(angle, angleStates, -maxAngle, maxAngle));
		}

	/* Reward function for the angle controller */
	public static double getRewardAngle(double angle, double vx, double vy) {

		/* TODO: IMPLEMENT THIS FUNCTION */
		//(10*(någonting mellan 0 och 1 där 1 är upp och 0 är ner))²
		return Math.pow(10*(1-Math.abs(angle)/maxAngle),2);
	}

	/* State discretization function for the full hover controller */
	public static String getStateHover(double angle, double vx, double vy) {

		/* TODO: IMPLEMENT THIS FUNCTION */
		String angleState = getStateAngle(angle, vx, vy);
		String vxState = String.valueOf(discretize(vx, vxStates, -maxVx, maxVx));
		String vyState = String.valueOf(discretize(vy, vyStates, -maxVy, maxVy));

		return angleState + ", " + vxState + ", " + vyState;
	}

	/* Reward function for the full hover controller */
	public static double getRewardHover(double angle, double vx, double vy) {

		double angleReward = getRewardAngle(angle, vx ,vy);
		//vx ska vara 0
		double vxReward = Math.pow(20*(1-Math.abs(vx)/maxVx),2);
		//vy ska vara 0
		double vyReward = Math.pow(30*(1-Math.abs(vy)/maxVy),2);
		/* TODO: IMPLEMENT THIS FUNCTION */
		
		
		return angleReward + vxReward + vyReward;
	}

	// ///////////////////////////////////////////////////////////
	// discretize() performs a uniform discretization of the
	// value parameter.
	// It returns an integer between 0 and nrValues-1.
	// The min and max parameters are used to specify the interval
	// for the discretization.
	// If the value is lower than min, 0 is returned
	// If the value is higher than min, nrValues-1 is returned
	// otherwise a value between 1 and nrValues-2 is returned.
	//
	// Use discretize2() if you want a discretization method that does
	// not handle values lower than min and higher than max.
	// ///////////////////////////////////////////////////////////
	public static int discretize(double value, int nrValues, double min,
			double max) {
		if (nrValues < 2) {
			return 0;
		}

		double diff = max - min;

		if (value < min) {
			return 0;
		}
		if (value > max) {
			return nrValues - 1;
		}

		double tempValue = value - min;
		double ratio = tempValue / diff;

		return (int) (ratio * (nrValues - 2)) + 1;
	}

	// ///////////////////////////////////////////////////////////
	// discretize2() performs a uniform discretization of the
	// value parameter.
	// It returns an integer between 0 and nrValues-1.
	// The min and max parameters are used to specify the interval
	// for the discretization.
	// If the value is lower than min, 0 is returned
	// If the value is higher than min, nrValues-1 is returned
	// otherwise a value between 0 and nrValues-1 is returned.
	// ///////////////////////////////////////////////////////////
	public static int discretize2(double value, int nrValues, double min,
			double max) {
		double diff = max - min;

		if (value < min) {
			return 0;
		}
		if (value > max) {
			return nrValues - 1;
		}

		double tempValue = value - min;
		double ratio = tempValue / diff;

		return (int) (ratio * nrValues);
	}

}
