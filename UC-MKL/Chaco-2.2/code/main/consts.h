// A PM is considered under-utilized if its CPU usage is below this limit.
const static int UNDER_UTILIZATION_THRESHOLD = 90;

// A PM is considered over-utilized if its CPU usage is above this limit.
const static int OVER_UTILIZATION_THRESHOLD = 110;

// Allow the last host to be under-utilized.
const static int MAX_UNDER_UTILIZED_HOST_COUNT = 1;

// Range of CPU Usage.
const static int MIN_CPU_PERCENT = 10;
const static int MAX_CPU_PERCENT = 100;

// Max number of rounds allowed.
const static int MAX_ITERATIONS = 1000;

// Usage decay coefficient. Should be a value in (0, 1].
const static double CURRENT_USAGE_WEIGHT = 0.6; 
