library(ggplot2)


#Create and store plots about the Average Upload/Download Bandwidth Usage
DownloadStats <- function(data, prefix) {
	maxTick = data$Tick[length(data$Tick)]
	tick <- 0:(maxTick*2-1)
	upRate <- 1:(maxTick*2)
	downRate <- 1:(maxTick*2)
	type <- 1:(maxTick*2)
	tftouUpRatio <- 1:(maxTick*2)
	tftouDownRatio <- 1:(maxTick*2)
	shareRatio <- 1:(maxTick*2)

#c("Tick","Type","Pid","Start","End","MaxUpload","MaxDownload","Upload","Download","MaxTFT","MaxOU","TFT","OU","TFTDown","TFTUp","OUDown","OUUp" )
	for(i in 0:(maxTick-1)){
	
		#Ignore Seeders
		#tick[i*2 + 1] <- i
		#type[i*2 +1] <- "Peer"
		#downRate[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") ,]$Download/data[(data$Tick == i) & (data$Type=="Peer"),]$MaxDownload )
		#upRate[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") ,]$Upload/data[(data$Tick == i) & (data$Type=="Peer"),]$MaxUpload )
		#tftouUpRatio[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") ,]$tftouUpRatio )
		#tftouDownRatio[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") ,]$tftouDownRatio )
		#shareRatio[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") ,]$shareRatio )
		
		#tick[i*2+1 + 1] <- i
		#type[i*2+1 + 1] <- "Peer_C1"
		#downRate[i*2+1 + 1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") ,]$Download/data[(data$Tick == i) & (data$Type=="Peer_C1"),]$MaxDownload )
		#upRate[i*2+1 + 1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") ,]$Upload/data[(data$Tick == i) & (data$Type=="Peer_C1"),]$MaxUpload )
		#tftouUpRatio[i*2+1 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") ,]$tftouUpRatio )
		#tftouDownRatio[i*2+1 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") ,]$tftouDownRatio )
		#shareRatio[i*2+1 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") ,]$shareRatio )
		
		tick[i*2 + 1] <- i
		type[i*2 +1] <- "Peer"
		downRate[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") & (data$End == -1),]$Download/data[(data$Tick == i) & (data$Type=="Peer") & (data$End == -1),]$MaxDownload )
		upRate[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") & (data$End == -1),]$Upload/data[(data$Tick == i) & (data$Type=="Peer") & (data$End == -1),]$MaxUpload )
		tftouUpRatio[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") & (data$End == -1),]$tftouUpRatio )
		tftouDownRatio[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") & (data$End == -1),]$tftouDownRatio )
		shareRatio[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") & (data$End == -1),]$shareRatio )
		
		tick[i*2+1 + 1] <- i
		type[i*2+1 + 1] <- "Peer_C1"
		downRate[i*2+1 + 1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") & (data$End == -1) ,]$Download/data[(data$Tick == i) & (data$Type=="Peer_C1") & (data$End == -1),]$MaxDownload )
		upRate[i*2+1 + 1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") & (data$End == -1),]$Upload/data[(data$Tick == i) & (data$Type=="Peer_C1") & (data$End == -1),]$MaxUpload )
		tftouUpRatio[i*2+1 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") & (data$End == -1),]$tftouUpRatio )
		tftouDownRatio[i*2+1 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") & (data$End == -1),]$tftouDownRatio )
		shareRatio[i*2+1 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") & (data$End == -1),]$shareRatio )
		
	
	}
	pData <- data.frame(tick, type, upRate, downRate, tftouUpRatio, tftouDownRatio, shareRatio )
	
	
	#Generate Plots
	pData.upload = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=upRate, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="Upload usage") + scale_color_manual( name="Peers (without seeders)", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )
	
	pData.download = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=downRate, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="Download usage") + scale_color_manual( name="Peers (without seeders)", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )
	
	pData.shareRatio = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=shareRatio, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="Download / Upload") + scale_color_manual( name="Peers (without seeders)", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") ) 

	pData.tftouUpRatio = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=tftouUpRatio, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="TFT/OU Upload") + scale_color_manual( name="Peers (without seeders)", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )
	pData.tftouDownRatio = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=tftouDownRatio, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="TFT/OU Download") + scale_color_manual( name="Peers (without seeders)", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )
	
	#Save Plots
	path = paste(prefix, "uploadRatio.png", sep="_")
	ggsave(file=path, plot = pData.upload, dpi=100)
	
	path = paste(prefix, "downloadRatio.png", sep="_")
	ggsave(file=path, plot=pData.download, dpi=100)

	path = paste(prefix, "shareRatio.png", sep="_")
	ggsave(file=path, plot=pData.shareRatio, dpi=100)
	
	path = paste(prefix, "tftouUpRatio.png", sep="_")
	ggsave(file=path, plot=pData.tftouUpRatio, dpi=100)

	path = paste(prefix, "tftouDownRatio.png", sep="_")
	ggsave(file=path, plot=pData.tftouDownRatio, dpi=100)
	
	return(pData)
}

#Create and store plots about the average number of TFT and OU Slots
ConnectionStats <- function(data)
{
	maxTick = data$Tick[length(data$Tick)]
	tick <- 0:(maxTick*2-1)
	type <- 1:(maxTick*2)
	avgTFT <- 1:(maxTick*2)
	avgOU <- 1:(maxTick*2)
	for(i in 0:(maxTick-1)){
		
		tick[i*2 + 1] <- i
		type[i*2 +1] <- "Peer"
		avgTFT[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") & (data$End == -1),]$TFT )
		avgOU[i*2 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer") & (data$End == -1),]$OU )
		
		tick[i*2+1 + 1] <- i
		type[i*2+1 + 1] <- "Peer_C1"
		avgTFT[i*2+1 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") & (data$End == -1),]$TFT )
		avgOU[i*2+1 +1] <- mean( data[ (data$Tick == i) & (data$Type=="Peer_C1") & (data$End == -1),]$OU )
	}
	pData <- data.frame(tick, type, avgTFT, avgOU )
	
	ouPlot = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=avgOU, colour=type) ) + xlab("Ticks") + ylab("OU Slots") + opts(title="Average number of OU Slots") + scale_color_manual( name="Peers (without seeders)", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )
	tftPlot = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=avgTFT, colour=type) ) + xlab("Ticks") + ylab("TFT Slots") + opts(title="Average number of TFT Slots") + scale_color_manual( name="Peers (without seeders)", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )

	path = paste(prefix, "Connections_OU.png", sep="_")
	ggsave(file=path , plot = ouPlot, dpi=100)

	path = paste(prefix, "Connections_TFT.png", sep="_")
	ggsave(file=path , plot=tftPlot, dpi=100)

	return(pData)
}


PeerCountStats <- function(data)
{
	maxTick = data$Tick[length(data$Tick)]
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

#Script has to be called like : Rscript Statistics.R  [STATS_FILE] [OUTPUT_DIR] [SUMMARY_FILE] [PREFIX] OR [SUMMARY_FILE] [SUMMART_OUTPUT_DIR] [PREFIX]
#Whereby STATS_FILE points to the csv input file and PREFIX will be

#Check arguments ( argument TRUE will filter all system arguments )
arg = commandArgs()

writeLines( paste("Received " , length(arg) , " arguments", sep="") )
writeLines( paste("Received args ... ", arg, sep="") )
#Own arguments start with arg[6]

if(length(arg) < 9){
	writeLines( "Missing arguments!" )
	#quit("no")
}

#writeLines("Enough arguments!")
#writeLines(paste("arg[6] ", arg[6], sep=""))

if( length(arg) == 8 ){
	dataFile = arg[6]
	outputDir = arg[7]
	prefix = arg[8]
	outputDir = paste( outputDir, prefix, sep="/")
	ecdfFile = paste( outputDir, "ECDF.png", sep="")
	histFile = paste( outputDir, "histogram.png", sep="")
	writeLines( "Assuming script was called to generate summary statistics!" )
	
	#Load data
	data = read.csv(dataFile, comment.char='#', sep=';', header=F )
	
	#Set col names
	colnames(data) <- c("Type","DownloadTime")
	
	#Create plot and store file
	hist = ggplot(data, aes(x=DownloadTime, fill=Type)) + xlab("Download time") + ylab("Peers") + geom_histogram(position=position_dodge()) + opts(title="Download time") + scale_fill_hue( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") )
	ggsave(file=histFile, plot=hist , dpi=100)
	
	#Create ECDF
	data.reduced = data[data$DownloadTime != -1, ] #Remove peers that did not complete their download
	#Adds a ecdf column to the data, containing the ecdf value for each line
	#Note: the ddply is used to group the data depening on the Type coloum ( so is like generating two tables, calculating ecdf for each and than join them again)
	data.reduced <- ddply(data.reduced, .(Type), transform , ecdf = ecdf(DownloadTime)(DownloadTime) )
	data.ecdf = ggplot(data=data.reduced) + geom_step(aes(x=DownloadTime, y=ecdf, color=Type) ) + xlab("Download Time") + ylab("ECDF") + opts(title="Download time") + scale_color_hue( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") )
	ggsave(file=ecdfFile, plot=data.ecdf , dpi=100)
}

if( length(arg) == 9)
{
	dataFile = arg[6]
	workingDir = arg[7]
	histFile = arg[8]
	prefix = arg[9]
	writeLines( paste("Assuming script was called to generate simulation statistics! On statistic data ", dataFile, " with histfile ", histFile , " and prefix ", prefix ,sep="") )
	
	setwd(workingDir)
	
	#Load data
	data = read.csv(dataFile, comment.char='#', sep=';', header=F )
	
	# Log format <Tick> <peer Type> <id> <downloadStart> <DownloadEnd> \
	#<Max Upload Rate> <Max Download Rate> <Current Upload Rate> <Current Download Rate> \
	#<Total # of max TFT Slots> <Total # of max OU Slots> <Total # of used TFT Slots> <Total # of used OU Slots>\n"
	
	#Name data
	colnames(data) <- c("Tick","Type","Pid","Start","End","MaxUpload","MaxDownload","Upload","Download","MaxTFT","MaxOU","TFT","OU","TFTDown","TFTUp","OUDown","OUUp" )
	
	#Calculate averages
	data$upUsage <- data$Upload / data$MaxUpload
	data$downUsage  <- data$Download / data$MaxDownload
	data$shareRatio <- data$Download / data$Upload
	data$tftouUpRatio <- data$TFTUp / data$OUUp
	data$tftouDownRatio <- data$TFTDown / data$OUDown
	
	#Remove irregularities , NaN and inf are set to zero
	data[ is.nan(data$tftouUpRatio),]$tftouUpRatio = 0
	data[ is.nan(data$tftouDownRatio),]$tftouDownRatio = 0
	data[ is.nan(data$shareRatio),]$shareRatio = 0
	data[ is.infinite(data$tftouUpRatio),]$tftouUpRatio = 0
	data[ is.infinite(data$tftouDownRatio),]$tftouDownRatio = 0
	data[ is.infinite(data$shareRatio),]$shareRatio = 0
	
	#DownloadStats(data, prefix)
	ConnectionStats(data)
	#PeerCountStats(data)
	#pData = DownloadTime(data, prefix)
	
	write.table(pData, file=histFile, sep=";", append=TRUE, col.names=FALSE, row.names = FALSE)
}