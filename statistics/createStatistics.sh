#!/bin/bash

if [ "$#" -eq 0 ]
then
	echo "No argument given, assuming script is called to generate images!"

	#Cleanup
	rm *.png *.Rout *.pdf

	R CMD BATCH downloadTime.R
	R CMD BATCH Conn.R
	R CMD BATCH peerCnt.R

	convert *.png stats.pdf
	rm *.Rout
	rm Rplots.pdf

elif [ "$1" == "clear" ]
then
	echo "Clearing directory!"
	rm *.png *.Rout *.pdf
fi
exit


