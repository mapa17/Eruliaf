library(ggplot2)


#Create and store plots about the Average Upload/Download Bandwidth Usage
DownloadStats <- function(data, prefix) {
	maxTick = max(data$Tick)
	tick <- 0:(maxTick*2-1)
	upRate <- 1:(maxTick*2)
	downRate <- 1:(maxTick*2)
	type <- 1:(maxTick*2)
	for(i in 0:(maxTick-1)){
		
		tick[i*2 + 1] <- i
		type[i*2 +1] <- "Peer"
		downRate[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") ,]$Download/data[(data$Tick == i) & (data$Type=="Peer"),]$MaxDownload )
		upRate[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") ,]$Upload/data[(data$Tick == i) & (data$Type=="Peer"),]$MaxUpload )
		
		tick[i*2+1 + 1] <- i
		type[i*2+1 + 1] <- "Peer_C1"
		downRate[i*2+1 + 1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") ,]$Download/data[(data$Tick == i) & (data$Type=="Peer_C1"),]$MaxDownload )
		upRate[i*2+1 + 1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") ,]$Upload/data[(data$Tick == i) & (data$Type=="Peer_C1"),]$MaxUpload )
	
	}
	pData <- data.frame(tick, type, upRate, downRate )
	
	upload = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=upRate, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="Upload usage") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )
	
	download = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=downRate, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="Download usage") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )
	
	path = paste(prefix, "uploadRatio.png", sep="_")
	ggsave(file=path, plot = upload, dpi=100)
	
	path = paste(prefix, "downloadRatio.png", sep="_")
	ggsave(file=path, plot=download, dpi=100)

	return(pData)
}

#Create and store plots about the average number of TFT and OU Slots
ConnectionStats <- function(data)
{
	maxTick = max(data$Tick)
	tick <- 0:(maxTick*2-1)
	type <- 1:(maxTick*2)
	avgTFT <- 1:(maxTick*2)
	avgOU <- 1:(maxTick*2)
	for(i in 0:(maxTick-1)){
		
		tick[i*2 + 1] <- i
		type[i*2 +1] <- "Peer"
		avgTFT[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") ,]$TFT )
		avgOU[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") ,]$OU )
		
		tick[i*2+1 + 1] <- i
		type[i*2+1 + 1] <- "Peer_C1"
		avgTFT[i*2+1 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") ,]$TFT )
		avgOU[i*2+1 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") ,]$OU )
	}
	pData <- data.frame(tick, type, avgTFT, avgOU )
	
	ouPlot = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=avgOU, colour=type) ) + xlab("Ticks") + ylab("OU Slots") + opts(title="Average number of OU Slots") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )
	tftPlot = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=avgTFT, colour=type) ) + xlab("Ticks") + ylab("TFT Slots") + opts(title="Average number of TFT Slots") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )

	path = paste(prefix, "Connections_OU.png", sep="_")
	ggsave(file=path , plot = ouPlot, dpi=100)

	path = paste(prefix, "Connections_TFT.png", sep="_")
	ggsave(file=path , plot=tftPlot, dpi=100)

	return(pData)
}


PeerCountStats <- function(data)
{
	maxTick = max(data$Tick)
	tick <- 0:(maxTick*2-1)
	type <- 1:(maxTick*2)
	online <- 1:(maxTick*2)
	completed <- 1:(maxTick*2)
	
	for(i in 0:(maxTick-1)){
		
		tick[i*2 + 1] <- i
		type[i*2 +1] <- "Peer"
		online[i*2 +1] <- nrow( data[ (data$Tick == i) & (data$Type=="Peer"), ] )
		completed[i*2 +1] <- nrow( data[ (data$Tick == i) & (data$Type=="Peer") & (data$End != -1), ] )
		
		tick[i*2+1 + 1] <- i
		type[i*2+1 + 1] <- "Peer_C1"
		online[i*2+1 +1] <- nrow( data[ (data$Tick == i) & (data$Type=="Peer_C1"), ] )
		completed[i*2+1 +1] <- nrow( data[ (data$Tick == i) & (data$Type=="Peer_C1") & (data$End != -1), ] )
	}
	pData <- data.frame(tick, type, online, completed )
	
	conn = ggplot(pData, aes(x=tick) ) + geom_area(aes(y=online, fill=type) , alpha=0.4 , position=position_identity() ) + geom_line( aes(y=completed, colour=type) ,position=position_identity()) + ylab("Peers") + xlab("Ticks") + opts(title="Total and completed Peers") + scale_fill_manual( name="Total Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") ) + scale_color_manual( name="Completed Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )
	
	path = paste(prefix, "Peer_Count.png", sep="_")
	ggsave(file=path , plot=conn, dpi=100)

	return(pData)
}

DownloadTime <- function(data, prefix)
{
	pIds = unique(data$Pid)
	nPeers = length(pIds)
	
	type <- 1:nPeers
	downloadTime <- 1:nPeers
	
	for(i in 1:(nPeers)){
		
		type[i] <- toString(unique(data[ (data$Pid == i), ]$Type))
		start <- unique(data[ (data$Pid == i), ]$Start)
		lastRound <- max(data[ (data$Pid == i), ]$Tick)
		end <- data[ (data$Tick == lastRound) & (data$Pid==i), ]$End
		if( end >= 0){
			downloadTime[i] <- end - start	
		} else {
			downloadTime[i] <- -1
		}
	}
	pData <- data.frame(type, downloadTime )
	
	hist = ggplot(pData, aes(x=downloadTime, fill=type)) + xlab("Download time [ticks]") + ylab("Peers") + geom_histogram(position=position_dodge()) + opts(title="Download time") + scale_fill_hue( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") )
	density = ggplot(pData, aes(x=downloadTime, colour=type)) + xlab("Download time [ticks]") + ylab("Peers [ratio]") + geom_density() + opts(title="Download time") + scale_colour_hue( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") )
	
	path = paste(prefix, "downloadTime_hist.png", sep="_")
	ggsave(file=path , plot=hist , dpi=100)
	
	path = paste( prefix, "downloadTime_den.png", sep="_")
	ggsave(file=path, plot=density , dpi=100)

	return(pData)
}

#Generate a copy of an vector v, with elment e insert at position pos ( index starting from 1 ) , pos = -1 appends e to the end
insert <- function(v, e, pos)
{
	if( pos == 1){
		return( c(e,v) )
	} else {
		if( pos > length(v) | (pos == -1) )
			pos = length(v)
		
		if( pos == length(v))
			return( c(v,e) )
		else
			return( c(v[1:(pos-1)],e,v[(pos):length(v)]))
	}
}

#Script has to be called like : R CMD BATCH --slave "--args [STATS_FILE] [HISTORY_OUTPUT_FILE] [PREFIX] OR [HISTORY_FILE]" Statistics.R
#Whereby STATS_FILE points to the csv input file and PREFIX will be

#Check arguments ( argument TRUE will filter all system arguments )
arg = commandArgs(TRUE)

writeLines( paste("Received args ... ", arg, sep="") )

if(length(arg) < 1){
	writeLines( "Missing argument! You have to specify the statistics file to load as first argument!" )
	quit("no")
}

if( length(arg) == 1 ){
	dataFile = arg[1]
	writeLines( paste("Assuming script was called to generate summary histogram! On hist data ", dataFile, sep="") )
	
	#Load data
	data = read.csv(dataFile, comment.char='#', sep=';', header=F )
	
	#Set col names
	colnames(data) <- c("Type","DownloadTime")
	
	#Create plot and store file
	hist = ggplot(data, aes(x=DownloadTime, fill=Type)) + xlab("Download time") + ylab("Peers") + geom_histogram(position=position_dodge()) + opts(title="Download time") + scale_fill_hue( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") )
	ggsave(file="hist_summary.png", plot=hist , dpi=100)
}

if( length(arg) == 3)
{
	dataFile = arg[1]
	histFile = arg[2]
	prefix = arg[3]
	writeLines( paste("Assuming script was called to generate simulation statistics! On statistic data ", dataFile, " with histfile ", histFile , " and prefix ", prefix ,sep="") )
	
	#Load data
	data = read.csv(dataFile, comment.char='#', sep=';', header=F )
	
	# Log format <Tick> <peer Type> <id> <downloadStart> <DownloadEnd> \
	#<Max Upload Rate> <Max Download Rate> <Current Upload Rate> <Current Download Rate> \
	#<Total # of max TFT Slots> <Total # of max OU Slots> <Total # of used TFT Slots> <Total # of used OU Slots>\n"
	
	#Name data
	colnames(data) <- c("Tick","Type","Pid","Start","End","MaxUpload","MaxDownload","Upload","Download","MaxTFT","MaxOU","TFT","OU" )
	
	#Calculate averages
	data$upRatio <- data$Upload / data$MaxUpload
	data$downRatio  <- data$Download / data$MaxDownload
	
	#DownloadStats(data)
	#ConnectionStats(data)
	#PeerCountStats(data)
	pData = DownloadTime(data, prefix)
	
	write.table(pData, file=histFile, sep=";", append=TRUE, col.names=FALSE, row.names = FALSE)
}