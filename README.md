Eurliaf - A BitTorrent like Overlay peer simulator
==================================================
2.2.2012

Dependencies
------------

python (>3.0)
imagemagic
R (>= 2.14)
ggplot2 (>0.9)

Install them using something like

`sudo apt-get install python3 r-base imagemagick`

`sudo R`

`> install.packages("ggplot2", dependencies = TRUE )`

`> quit("no")`

Usage
-----

A Simple call to the Simulation Pipeline ( which will generate simulation files, run the simulation and generate
statistics ) is the following:

`python3 Simulation_Pipeline.py [PATH to simulation file]`

interesting program parameters are

-l ... disables the generation of log files ( can get really big! )
-p [PREFIX] ... puts PREFIX infront of all output files
-s ... will NOT run the simulation, but will read any simulation output and generate statistics ( is useful if generating
statistics failed in a previous run )

A tipical execution scenario is the following: 

`find configs/simulations/ -name 4x4_dynamic*1000MB* > runlist`
`cat runlist | xargs -i -n1 python3 Simulation_Pipeline.py -p V10_ -l {} >> run.log 2>&1 &`

This will generate a list of simulations to run, storing them in the file runlist
Each simulation file will be passed to the Pipeline, with a prefix of V10_ and the generation of log files is suppressed.
All output generated during execution is piped into run.log

Blame
-----

Author: Pasieka Manuel , mapa17@posgrado.upv.es
