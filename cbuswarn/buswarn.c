#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include "header.h"

//NOTE: TESTING ONLY, REMOVE FOR PRODUCTION
#include <time.h>

//format: a schedule distributor program will provide a .dat file
//with the following format:
//
//(num rows) (num stops (columns)) \n
//t1 t2 t3...
//
//note: all times are in seconds since epoch. 
//hopefully these won't be running in 2038
//
//CHIP: Arduino Pro Mini
//WIFI CHIP: ESP 8266? must support WEP2 enterprise
//RTC CHIP: any

int main()
{
	size_t schedLen  = 0;
	int* sched = loadSched(&schedLen);
	int waitTime = 100;
	int newWaitTime = 101;
	int cTime = currentTime();
	int stopIndex = 0;
	//printf("%d\n", currentTime());

	/* logic
	 * at increments of 5s (too high? 3s) check 
	 * is the current time > the current stop on the schedule?
	 * if so, change the current stop to the next stop
	 */

	cTime = currentTime(); //so we only access the RTC once
	while(stopIndex<schedLen)
	{
		//printf("%d of %d\n", stopIndex, schedLen);
		sleep(1); //3 seconds
		cTime += 1;
		if(cTime  > sched[stopIndex])
		{
			++stopIndex;
			//change wait time 
		}

		newWaitTime = calcWaitTime(cTime, sched[stopIndex]);

		if(newWaitTime != waitTime)
		{
			waitTime = newWaitTime;
			display(waitTime);
		}
	}

	//atexit(free(sched) );
	free(sched);
}

int* loadSched(size_t *timesLen)
{
	//contained in here will probably be the methods that setup wifi and mqtt. 
	//there's no filesystem in the arduino, which could make things difficult. 
	//but I BELIEVE!

	int num1 = 0;
	int numStops, numRows;

	//the type that fileptr points to is a FILE
	//using the constant FILENAME
	FILE *fileptr = fopen(FILENAME, "r");

	fscanf(fileptr, "%d %d", &numRows, &numStops); //why the &? need the ADDRESS of the variable

	//filling the list up
	int data[numRows][numStops];
	int* times = malloc(numRows * sizeof(int));

	if(times == NULL)
	{
		printf("Error: could not malloc size of %d.\n", numRows *sizeof(int));
		exit(1);
	}

	for(int j = 0; j<numRows;j++)
	{
		for(int i = 0; i<numStops; i++)
		{
			fscanf(fileptr, "%d", &data[j][i]);
			//printf("%d\n", data[j][i]);
		}
		times[j] = data[j][MYSTOP];
		//printf("%d\n", times[j]);
	}

	*timesLen = numRows; //keeping track of length 
	return times;
}

int currentTime()
{
	//This will eventually interface with the RTC chip
	return time(0);
	//return 1602968400 + 3600;
}

int calcWaitTime(int cTime, int stopTime)
{
	return ceill((stopTime-cTime)/60);
	//why ceill? seems more accurate than floor
}

int display(int data)
{
	//will be used for the screen eventually
	//but for now, just a print statement
	printf("%d\n", data);
	return 0;
}
