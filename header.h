//for error checking and debugging
const char STATNAME[] = "Aggie Station";
const char* FILENAME = "times.dat";
const int MYSTOP = 2;

int* loadSched();
int currentTime();
int displayWaitTime();
int calcWaitTime();
int display();
