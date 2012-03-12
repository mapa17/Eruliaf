#!/bin/bash

if [ "$#" -eq 0 ]
then
	echo "No argument given, assuming script is called to generate images!"

	#Cleanup
	rm *.png *.Rout *.pdf 2>/dev/null

	R CMD BATCH Statistics.R

	convert *.png Statistic_Summary.pdf
	rm *.Rout Rplots.pdf 2>/dev/null

	echo "Created pdf Statistic_Summary.pdf"

elif [ "$1" == "clear" ]
then
	echo "Clearing directory!"
	rm *.csv *.png *.Rout *.pdf 2>/dev/null
fi
exit


