library(ggplot2)
library(scales)
library(plyr)

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
	
	o = opts(legend.position="bottom", title="Download time")
	g = guide_legend(title.position="left" , direction="horizontal" )
	sf = scale_fill_hue( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , guide=g)
	
	hist = ggplot(pData, aes(x=downloadTime, fill=type)) + xlab("Download time [ticks]") + ylab("Peers") + geom_histogram(position=position_dodge()) + sf + o 
	density = ggplot(pData, aes(x=downloadTime, colour=type)) + xlab("Download time [ticks]") + ylab("Peers [ratio]") + geom_density() + sf + o 
	
	path = paste(prefix, "downloadTime_hist.png", sep="_")
	ggsave(file=path , plot=hist , dpi=100)
	
	path = paste( prefix, "downloadTime_den.png", sep="_")
	ggsave(file=path, plot=density , dpi=100)

	return(pData)
}

proccessData <- function(data, prefix)
{
	maxTick = data$Tick[length(data$Tick)]
	tick <- 0:(maxTick*2-1)
	type <- 1:(maxTick*2)
	online <- 1:(maxTick*2)
	completed <- 1:(maxTick*2)
	avgnTFTSlots <- 1:(maxTick*2)
	avgnOUSlots <- 1:(maxTick*2)
	upRate <- 1:(maxTick*2)
	downRate <- 1:(maxTick*2)
	type <- 1:(maxTick*2)
	tftouUpRatio <- 1:(maxTick*2)
	tftouDownRatio <- 1:(maxTick*2)
	shareRatio <- 1:(maxTick*2)
	minNPieces <-  1:(maxTick*2)
	maxNPieces <-  1:(maxTick*2)
	meanNPieces <-  1:(maxTick*2)
	sdNPieces <-  1:(maxTick*2)
	nConnections <-  1:(maxTick*2)
	sdNConnections <- 1:(maxTick*2)
	
	#Seperate the frame depending on type and completed or downloading peers
	dP = data[ (data$Type=="Peer"), ]
	dPr = dP[ (dP$End == -1), ]
	dPC1 = data[ (data$Type=="Peer_C1"), ]
	dPC1r = dPC1[ (dPC1$End == -1), ]
	for(i in 0:(maxTick-1)){
		
		#Get a subtable for this tick only
		dPt = dP[ (dP$Tick == i), ]
		dPrt = dPr[ (dPr$Tick == i), ]
		tick[i*2 + 1] <- i
		type[i*2 +1] <- "Peer"
		online[i*2 +1] <- nrow( dPt )
		completed[i*2 +1] <- nrow( dPt[ (dPt$End != -1) , ] )
		avgnTFTSlots[i*2 +1] <- mean( dPrt$TFT )
		avgnOUSlots[i*2 +1] <- mean( dPrt$OU )
		downRate[i*2 +1] <- mean( dPrt$Download/dPrt$MaxDownload )
		upRate[i*2 +1] <- mean( dPrt$Upload/dPrt$MaxUpload )
		tftouUpRatio[i*2 +1] <- mean( dPrt$tftouUpRatio , na.rm = TRUE)
		tftouDownRatio[i*2 +1] <- mean( dPrt$tftouDownRatio , na.rm = TRUE)
		shareRatio[i*2 +1] <- mean( dPrt$shareRatio , na.rm = TRUE)
		#minNPieces[i*2 +1] <- min(dPrt$nDownloadedPieces)
		#maxNPieces[i*2 +1] <- max(dPrt$nDownloadedPieces)
		meanNPieces[i*2 +1] <- mean(dPrt$nDownloadedPieces)
		sdNPieces[i*2 +1] <- sd(dPrt$nDownloadedPieces)
		nConnections[i*2 +1] <- mean(dPrt$nConnections)
		sdNConnections[i*2 +1] <- sd(dPrt$nConnections)
		
		#Get a subtable for this tick only
		dPC1t = dPC1[ (dPC1$Tick == i), ]
		dPC1rt = dPC1r[ (dPC1r$Tick == i), ]
		tick[i*2+1 + 1] <- i
		type[i*2+1 + 1] <- "Peer_C1"
		online[i*2+1 +1] <- nrow( dPC1t )
		completed[i*2+1 +1] <- nrow( dPC1t[ (dPC1t$End != -1), ] )
		avgnTFTSlots[i*2+1 +1] <- mean( dPC1rt$TFT )
		avgnOUSlots[i*2+1 +1] <- mean( dPC1rt$OU )
		downRate[i*2+1 + 1] <- mean( dPC1rt$Download/dPC1rt$MaxDownload )
		upRate[i*2+1 + 1] <- mean( dPC1rt$Upload/dPC1rt$MaxUpload )
		tftouUpRatio[i*2+1 +1] <- mean( dPC1rt$tftouUpRatio , na.rm = TRUE)
		tftouDownRatio[i*2+1 +1] <- mean( dPC1rt$tftouDownRatio , na.rm = TRUE)
		shareRatio[i*2+1 +1] <- mean( dPC1rt$shareRatio , na.rm = TRUE)
		#minNPieces[i*2+1 +1] <- min(dPC1rt$nDownloadedPieces)
		#maxNPieces[i*2+1 +1] <- max(dPC1rt$nDownloadedPieces)
		meanNPieces[i*2+1 +1] <- mean(dPC1rt$nDownloadedPieces)
		sdNPieces[i*2+1 +1] <- sd(dPC1rt$nDownloadedPieces)
		nConnections[i*2+1 +1] <- mean(dPC1rt$nConnections)
		sdNConnections[i*2+1 +1] <- sd(dPC1rt$nConnections)
	}
	
	#Remove irregularities , NaN and inf are set to zero
	fv = is.nan(shareRatio)
	if( TRUE %in% fv) shareRatio[fv] = 0
	fv = is.infinite(shareRatio)
	if( TRUE %in% fv) shareRatio[fv] = 0

	fv = is.nan(tftouDownRatio)
	if( TRUE %in% fv) tftouDownRatio[fv] = 0
	fv = is.infinite(tftouDownRatio)
	if( TRUE %in% fv) tftouDownRatio[fv] = 0
	
	fv = is.nan(tftouUpRatio)
	if( TRUE %in% fv) tftouUpRatio[fv] = 0
	fv = is.infinite(tftouUpRatio)
	if( TRUE %in% fv) tftouUpRatio[fv] = 0
	
	pData <- data.frame(tick, type, online, completed, avgnTFTSlots, avgnOUSlots, upRate, downRate, tftouUpRatio, tftouDownRatio, shareRatio, minNPieces, maxNPieces, meanNPieces, sdNPieces, nConnections, sdNConnections)
	pData$lsdNPieces <- pData$meanNPieces - pData$sdNPieces
	pData$usdNPieces <- pData$meanNPieces + pData$sdNPieces
	pData$lsdNConnections <- pData$nConnections - pData$sdNConnections
	pData$usdNConnections <- pData$nConnections + pData$sdNConnections
	
	#Prepare legends
	o = opts(legend.position="bottom")
	g = guide_legend(title.position="left" , direction="horizontal" )
	cm = scale_color_manual( name="Peers\n(without seeders)", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g )
	
	fm = scale_fill_manual( name="Total Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g) 
	cm2 = scale_color_manual( name="Completed Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g )
	
	cm3 = scale_color_manual( name="Number of Pieces" , breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g )
	fm3 = scale_fill_manual( name="Standard deviation", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g)
	
	cm4 = scale_color_manual( name="# connected Peers" , breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g )
	fm4 = scale_fill_manual( name="Standard deviation", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g)
	
	#Generate Plots
	pData.pieceAvailability = ggplot(pData, aes(x=tick) ) + ylab("# Pieces") + xlab("Ticks") + opts(title="Piece availability") + fm3 + cm3 + o + geom_smooth(aes(y=meanNPieces, ymin = lsdNPieces, ymax = usdNPieces, colour=type, fill=type), data=pData, stat="identity")
	
	pData.neighbourhoodSize = ggplot(pData, aes(x=tick) ) + ylab("# Peers") + xlab("Ticks") + opts(title="Neighbourhood size") + fm4 + cm4 + o + geom_smooth(aes(y=nConnections, ymin = lsdNConnections, ymax = usdNConnections, colour=type, fill=type), data=pData, stat="identity")
	
	pData.upload = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=upRate, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="Upload usage") + cm + o 
	
	pData.download = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=downRate, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="Download usage") + cm + o
	
	pData.shareRatio = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=shareRatio, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="Download / Upload") + cm + o 
	
	pData.tftouUpRatio = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=tftouUpRatio, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="TFT/OU Upload") + cm + o
	pData.tftouDownRatio = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=tftouDownRatio, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="TFT/OU Download") + cm + o

	pData.connPlot = ggplot(pData, aes(x=tick) ) + geom_area(aes(y=online, fill=type) , alpha=0.4 , position="identity" ) + geom_line( aes(y=completed, colour=type) ,position="identity") + ylab("Peers") + xlab("Ticks") + opts(title="Total and completed Peers") + fm + cm2 + o
	pData.ouPlot = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=avgnOUSlots, colour=type) ) + xlab("Ticks") + ylab("OU Slots") + opts(title="Average number of OU Slots") + cm + o
	pData.tftPlot = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=avgnTFTSlots, colour=type) ) + xlab("Ticks") + ylab("TFT Slots") + opts(title="Average number of TFT Slots") + cm + o
	
	
	#Save Plots	
	path = paste(prefix, "Connections_OU.png", sep="_")
	ggsave(file=path , plot=pData.ouPlot, dpi=100)
	
	path = paste(prefix, "Connections_TFT.png", sep="_")
	ggsave(file=path , plot=pData.tftPlot, dpi=100)
	
	path = paste(prefix, "Peer_Count.png", sep="_")
	ggsave(file=path , plot=pData.connPlot, dpi=100)

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
	
	path = paste(prefix, "pieceAvailability.png", sep="_")
	ggsave(file=path, plot=pData.pieceAvailability, dpi=100)
	
	path = paste(prefix, "neighbourHoodSize.png", sep="_")
	ggsave(file=path, plot=pData.neighbourhoodSize, dpi=100)
	
	
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

if(length(arg) < 8){
	writeLines( "Missing arguments!" )
	quit("no")
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
	colnames(data) <- c("Type", "DownloadTime")
	
	
	o = opts(legend.position="bottom")
	g = guide_legend(title.position="left" , direction="horizontal" )
	sf = scale_fill_hue( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , guide=g)
	#Create plot and store file
	hist = ggplot(data, aes(x=DownloadTime, fill=Type)) + xlab("Download time") + ylab("Peers") + geom_histogram(position=position_dodge()) + opts(title="Download time") + sf + o  
	ggsave(file=histFile, plot=hist , dpi=100)
	
	#Create ECDF
	data.reduced = data[data$DownloadTime != -1, ] #Remove peers that did not complete their download
	#Adds a ecdf column to the data, containing the ecdf value for each line
	#Note: the ddply is used to group the data depening on the Type coloum ( so is like generating two tables, calculating ecdf for each and than join them again)
	data.reduced <- ddply(data.reduced, .(Type), transform , ecdf = ecdf(DownloadTime)(DownloadTime) )
	
	sc = scale_color_hue( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , guide=g)
	data.ecdf = ggplot(data=data.reduced) + geom_step(aes(x=DownloadTime, y=ecdf, color=Type) ) + xlab("Download Time") + ylab("ECDF") + opts(title="Download time") + sc + o 
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
	
	# Log format :
	#<Tick> <peer Type> <id> <downloadStart> <DownloadEnd>
	#<Max Upload Rate> <Max Download Rate> <Current Upload Rate> <Current Download Rate>
	#<Total # of max TFT Slots> <Total # of max OU Slots> <Total # of used TFT Slots> <Total # of used OU Slots>
	#<Total #Bytes TFT Download> <Total #Bytes TFT Upload> <Total #Bytes OU Download> <Total #Bytes OU Upload>
	#<# Downloaded pieces><# Total Pieces>
	#<# of connected Peers>
	
	#Name data
	colnames(data) <- c("Tick","Type","Pid","Start","End","MaxUpload","MaxDownload","Upload","Download","MaxTFT","MaxOU","TFT","OU","TFTDown","TFTUp","OUDown","OUUp", "nDownloadedPieces", "nTotalPieces", "nConnections" )
	
	#Calculate averages
	data$upUsage <- data$Upload / data$MaxUpload
	data$downUsage  <- data$Download / data$MaxDownload
	data$shareRatio <- data$Download / data$Upload
	data$tftouUpRatio <- data$TFTUp / data$OUUp
	data$tftouDownRatio <- data$TFTDown / data$OUDown
	
	#Remove irregularities , NaN and inf are set to zero
	fv = is.nan(data$tftouUpRatio)
	if( TRUE %in% fv) data[ fv,]$tftouUpRatio = 0
	
	fv = is.nan(data$tftouDownRatio)
	if( TRUE %in% fv)	data[ fv,]$tftouDownRatio = 0
	
	fv = is.nan(data$shareRatio)
	if( TRUE %in% fv)	data[ fv,]$shareRatio = 0

	fv = is.infinite(data$tftouUpRatio)
	if( TRUE %in% fv)	data[ fv,]$tftouUpRatio = 0
	
	fv = is.infinite(data$tftouDownRatio)
	if( TRUE %in% fv)	data[ fv,]$tftouDownRatio = 0
	
	fv = is.infinite(data$shareRatio)
	if( TRUE %in% fv)	data[ fv,]$shareRatio = 0
	
	
	#Filter too high values
	m = mean(data$shareRatio) * 10
	fv = ((data$shareRatio) >= m)
	if( TRUE %in% fv)	data[ fv,]$shareRatio = NA
	
	m = mean(data$tftouUpRatio) * 10
	fv = ((data$tftouUpRatio) >= m)
	if( TRUE %in% fv)	data[ fv,]$tftouUpRatio = NA

	m = mean(data$tftouDownRatio) * 10
	fv = ((data$tftouDownRatio) >= m)
	if( TRUE %in% fv)	data[ fv,]$tftouDownRatio = NA
	

	#Do processing and generate Plots
	proccessData(data, prefix)
	pData = DownloadTime(data, prefix)
	
	#Save the processed data into the summary file
	write.table(pData, file=histFile, sep=";", append=TRUE, col.names=FALSE, row.names = FALSE)
}