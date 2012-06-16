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
		pid = pIds[i] #Iterate the pIds list . Fixing issue #76
		#writeLines( paste("Processing peer ", pid ,sep="") )
		
		type[i] <- toString(unique(data[ (data$Pid == pid), ]$Type))
		start <- unique(data[ (data$Pid == pid), ]$Start)
		lastRound <- max(data[ (data$Pid == pid), ]$Tick)
		end <- data[ (data$Tick == lastRound) & (data$Pid==pid), ]$End
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

proccessData <- function(data)
{
	maxTick = data$Tick[length(data$Tick)]
	tick <- 0:(maxTick*2-1)
	type <- 1:(maxTick*2)
	online <- 1:(maxTick*2)
	completed <- 1:(maxTick*2)
	avgnTFTSlots <- 1:(maxTick*2)
	avgnOUSlots <- 1:(maxTick*2)
	#upRate <- 1:(maxTick*2)
	#downRate <- 1:(maxTick*2)
	type <- 1:(maxTick*2)
	tftUpRate <- 1:(maxTick*2)
	ouUpRate <- 1:(maxTick*2)
	tftDownRate <- 1:(maxTick*2)
	ouDownRate <- 1:(maxTick*2)
	tftouUpRatio <- 1:(maxTick*2)
	tftouDownRatio <- 1:(maxTick*2)
	shareRatio <- 1:(maxTick*2)
	minNPieces <- 1:(maxTick*2)
	maxNPieces <- 1:(maxTick*2)
	meanNPieces <- 1:(maxTick*2)
	sdNPieces <- 1:(maxTick*2)
	nConnections <- 1:(maxTick*2)
	sdNConnections <- 1:(maxTick*2)
	maxDownload <- 1:(maxTick*2)
	maxUpload <- 1:(maxTick*2)
	download <- 1:(maxTick*2)
	upload <- 1:(maxTick*2)
	seederupload <- 1:(maxTick*2)
	seedermaxUpload <- 1:(maxTick*2)
	
	#Seperate the frame depending on type and completed or downloading peers
	dP = data[ (data$Type=="Peer"), ]
	dPs = dP[ (dP$End != -1), ] #Seeders
	dPr = dP[ (dP$End == -1), ] #Downloaders
	dPC1 = data[ (data$Type=="Peer_C1"), ]
	dPC1s = dPC1[ (dPC1$End != -1), ]
	dPC1r = dPC1[ (dPC1$End == -1), ]
	
	lowerLimit = 0
	upperLimit = 0
	#Calculate means and other values for two types of peers and every tick
	for(i in 0:(maxTick-1)){
		
		#Get a subtable for this tick only
		dPt = dP[ (dP$Tick == i), ]
		dPst = dP[ (dPs$Tick == i), ]
		dPrt = dPr[ (dPr$Tick == i), ]
		if(length(dPrt$Tick) > 0)
			upperLimit = i
		
		tick[i*2 + 1] <- i
		type[i*2 +1] <- "Peer"
		online[i*2 +1] <- nrow( dPt )
		seederupload[i*2 +1] <- mean( dPst$Upload , na.rm = TRUE)
		seedermaxUpload[i*2 +1] <- mean( dPst$MaxUpload , na.rm = TRUE )
		completed[i*2 +1] <- nrow( dPt[ (dPt$End != -1) , ] )
		
		avgnTFTSlots[i*2 +1] <- mean( dPrt$TFT )
		avgnOUSlots[i*2 +1] <- mean( dPrt$OU )
		maxDownload[i*2 +1] <- mean( dPrt$MaxDownload , na.rm = TRUE)
		maxUpload[i*2 +1] <- mean( dPrt$MaxUpload , na.rm = TRUE )
		download[i*2 +1] <- mean( dPrt$Download , na.rm = TRUE)
		upload[i*2 +1] <- mean( dPrt$Upload , na.rm = TRUE)
		tftUpRate[i*2 +1] <- mean( dPrt$TFTUp )
		tftDownRate[i*2 +1] <- mean( dPrt$TFTDown )
		ouUpRate[i*2 +1] <- mean( dPrt$OUUp )
		ouDownRate[i*2 +1] <- mean( dPrt$OUDown , na.rm = TRUE )
		tftouUpRatio[i*2 +1] <- mean( dPrt$tftouUpRatio , na.rm = TRUE)
		tftouDownRatio[i*2 +1] <- mean( dPrt$tftouDownRatio , na.rm = TRUE)
		shareRatio[i*2 +1] <- mean( dPrt$shareRatio , na.rm = TRUE)
		#minNPieces[i*2 +1] <- min(dPrt$nDownloadedPieces)
		#maxNPieces[i*2 +1] <- max(dPrt$nDownloadedPieces)
		meanNPieces[i*2 +1] <- mean(dPrt$nDownloadedPieces)
		sdNPieces[i*2 +1] <- sd(dPrt$nDownloadedPieces)
		nConnections[i*2 +1] <- mean(dPrt$nConnections , na.rm = TRUE)
		sdNConnections[i*2 +1] <- sd(dPrt$nConnections , na.rm = TRUE)
		
		#Get a subtable for this tick only
		dPC1t = dPC1[ (dPC1$Tick == i), ]
		dPC1st = dPC1[ (dPC1s$Tick == i), ]
		dPC1rt = dPC1r[ (dPC1r$Tick == i), ]
		if(length(dPC1rt$Tick) > 0)
			upperLimit = i
		
		
		tick[i*2+1 + 1] <- i
		type[i*2+1 + 1] <- "Peer_C1"
		online[i*2+1 +1] <- nrow( dPC1t )
		seederupload[i*2+1 +1] <- mean( dPC1st$Upload , na.rm = TRUE)
		seedermaxUpload[i*2+1 +1] <- mean( dPC1st$MaxUpload , na.rm = TRUE )
		completed[i*2+1 +1] <- nrow( dPC1t[ (dPC1t$End != -1), ] )
		
		avgnTFTSlots[i*2+1 +1] <- mean( dPC1rt$TFT )
		avgnOUSlots[i*2+1 +1] <- mean( dPC1rt$OU )
		download[i*2+1 + 1] <- mean( dPC1rt$Download , na.rm = TRUE)
		upload[i*2+1 + 1] <- mean( dPC1rt$Upload , na.rm = TRUE)
		tftUpRate[i*2+1 + 1] <- mean( dPC1rt$TFTUp )
		tftDownRate[i*2+1 + 1] <- mean( dPC1rt$TFTDown )
		ouUpRate[i*2+1 + 1] <- mean( dPC1rt$OUUp )
		ouDownRate[i*2+1 + 1] <- mean( dPC1rt$OUDown )
		tftouUpRatio[i*2+1 +1] <- mean( dPC1rt$tftouUpRatio , na.rm = TRUE)
		tftouDownRatio[i*2+1 +1] <- mean( dPC1rt$tftouDownRatio , na.rm = TRUE)
		shareRatio[i*2+1 +1] <- mean( dPC1rt$shareRatio , na.rm = TRUE)
		#minNPieces[i*2+1 +1] <- min(dPC1rt$nDownloadedPieces)
		#maxNPieces[i*2+1 +1] <- max(dPC1rt$nDownloadedPieces)
		meanNPieces[i*2+1 +1] <- mean(dPC1rt$nDownloadedPieces)
		sdNPieces[i*2+1 +1] <- sd(dPC1rt$nDownloadedPieces)
		nConnections[i*2+1 +1] <- mean(dPC1rt$nConnections)
		sdNConnections[i*2+1 +1] <- sd(dPC1rt$nConnections)
		maxDownload[i*2+1 +1] <- mean( dPC1rt$MaxDownload , na.rm = TRUE)
		maxUpload[i*2+1 +1] <- mean( dPC1rt$MaxUpload , na.rm = TRUE)
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
	
	pData <- data.frame(tick, type, online, completed, avgnTFTSlots, avgnOUSlots, tftouUpRatio,
		tftouDownRatio, shareRatio, minNPieces, maxNPieces, meanNPieces, sdNPieces, nConnections, sdNConnections,
		tftUpRate, tftDownRate, ouUpRate, ouDownRate, maxDownload, maxUpload, upload, download, seederupload, seedermaxUpload)

	pData.lowerLimit <- lowerLimit
	pData.upperLimit <- upperLimit

	pData$lsdNPieces <- pData$meanNPieces - pData$sdNPieces
	pData$usdNPieces <- pData$meanNPieces + pData$sdNPieces
	pData$lsdNConnections <- pData$nConnections - pData$sdNConnections
	pData$usdNConnections <- pData$nConnections + pData$sdNConnections
	
	pData$downRate <- pData$download / pData$maxDownload
	pData$upRate <- pData$upload / pData$maxUpload
	pData$seederupRate <- pData$seederupload / pData$seedermaxUpload

	#Scale to maximum up/down rate
	pData$tftUpRate <- pData$tftUpRate/pData$maxUpload
	pData$ouUpRate <- pData$ouUpRate/pData$maxUpload
	pData$tftDownRate <- pData$tftDownRate/pData$maxDownload
	pData$ouDownRate <- pData$ouDownRate/pData$maxDownload
		
	return( list(data=pData, ll=lowerLimit, ul=upperLimit) )
}



createPlots <- function(pData, lowerLimit, upperLimit)
{
	#Prepare legends
	o = opts(legend.position="bottom")
	sc = scale_x_continuous(limits = c(lowerLimit, upperLimit))
	g = guide_legend(title.position="left" , direction="horizontal" )
	cm = scale_color_manual( name="Peers\n(without seeders)", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g )
	
	fm = scale_fill_manual( name="Total Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g) 
	cm2 = scale_color_manual( name="Completed Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g )
	
	cm3 = scale_color_manual( name="Number of Pieces" , breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g )
	fm3 = scale_fill_manual( name="Standard deviation", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g)
	
	cm4 = scale_color_manual( name="# connected Peers" , breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g )
	fm4 = scale_fill_manual( name="Standard deviation", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") , guide=g)
	
	s = stat_smooth()
	 
	
	#Generate Plots
	pData.pieceAvailability = ggplot(pData, aes(x=tick) ) + ylab("# Pieces") + xlab("Ticks") + opts(title="Local Piece availability") + fm3 + cm3 + o + geom_smooth(aes(y=meanNPieces, ymin = lsdNPieces, ymax = usdNPieces, colour=type, fill=type), data=pData, stat="identity") + sc
	
	pData.NeighbourHoodSize = ggplot(pData, aes(x=tick) ) + ylab("# Peers") + xlab("Ticks") + opts(title="Neighbourhood size") + fm4 + cm4 + o + geom_smooth(aes(y=nConnections, ymin = lsdNConnections, ymax = usdNConnections, colour=type, fill=type), data=pData, stat="identity") + sc
	
	pData.upload = ggplot(pData, aes(x=tick, y=upRate, colour=type) ) + geom_line() + xlab("Ticks") + ylab("Ratio to maximum Upload") + opts(title="Upload usage") + cm + o + s + sc
	pData.download = ggplot(pData, aes(x=tick, y=downRate, colour=type) ) + geom_line() + xlab("Ticks") + ylab("Ratio to maximum Download") + opts(title="Download usage") + cm + o + s + sc
	
	#This plot throws errors if there are too many NaN values in seederupRate because of no seeders , produce a reduced data set with containing only valid data
	fv <- is.nan(pData$seederupRate)
	redTick <- pData[fv == FALSE,]$tick
	redUpRate <- pData[fv == FALSE,]$seederupRate
	redType <- pData[fv == FALSE,]$type
	reducedData <- data.frame(redTick, redUpRate,redType)
	colnames(reducedData) <- c("tick", "seederupRate", "type") 
	pData.seederupload = ggplot(reducedData, aes(x=tick, y=seederupRate, colour=type) ) + geom_line() + xlab("Ticks") + ylab("Ratio to maximum Upload") + opts(title="Seeder Upload usage") + cm2 + o + s + sc
	
	pData.TFTUploadRate = ggplot(pData, aes(x=tick , y=tftUpRate, colour=type) ) + geom_line() + xlab("Ticks") + ylab("Ratio to maximum Upload") + opts(title="TFT Upload Rate") + cm + o + s + sc
	pData.OUUploadRate = ggplot(pData, aes(x=tick, y=ouUpRate, colour=type) ) + geom_line() + xlab("Ticks") + ylab("Ratio to maximum Upload") + opts(title="OU Upload Rate") + cm + o + s + sc
	
	pData.TFTDownloadRate = ggplot(pData, aes(x=tick, y=tftDownRate, colour=type) ) + geom_line() + xlab("Ticks") + ylab("Ratio to maximum Download") + opts(title="TFT Download Rate") + cm + o + s + sc 
	pData.OUDownloadRate = ggplot(pData, aes(x=tick, y=ouDownRate, colour=type) ) + geom_line() + xlab("Ticks") + ylab("Ratio to maximum Download") + opts(title="OU Download Rate") + cm + o + s + sc
	
	pData.shareRatio = ggplot(pData, aes(x=tick, y=shareRatio, colour=type) ) + geom_line() + xlab("Ticks") + ylab("Ratio") + opts(title="Download / Upload Ratio") + cm + o + s + sc 
	
	pData.tftouUpRatio = ggplot(pData, aes(x=tick, y=tftouUpRatio, colour=type) ) + geom_line() + xlab("Ticks") + ylab("Ratio") + opts(title="TFT/OU Upload Ratio") + cm + o + s + sc
	pData.tftouDownRatio = ggplot(pData, aes(x=tick, y=tftouDownRatio, colour=type) ) + geom_line() + xlab("Ticks") + ylab("Ratio") + opts(title="TFT/OU Download Ratio") + cm + o + s + sc
	
	pData.connPlot = ggplot(pData, aes(x=tick) ) + geom_area(aes(y=online, fill=type) , alpha=0.4 , position="identity" ) + geom_line( aes(y=completed, colour=type) ,position="identity") + ylab("Peers") + xlab("Ticks") + opts(title="Total and completed Peers") + fm + cm2 + o
	pData.ouPlot = ggplot(pData, aes(x=tick, y=avgnOUSlots, colour=type) ) + geom_line() + xlab("Ticks") + ylab("OU Slots") + opts(title="Average number of OU Slots") + cm + o + s + sc
	pData.tftPlot = ggplot(pData, aes(x=tick, y=avgnTFTSlots, colour=type) ) + geom_line() + xlab("Ticks") + ylab("TFT Slots") + opts(title="Average number of TFT Slots") + cm + o + s + sc
	
	
	#Save Plots	
	path = paste(prefix, "Connections_OU.png", sep="_")
	ggsave(file=path , plot=pData.ouPlot, dpi=100)
	
	path = paste(prefix, "Connections_TFT.png", sep="_")
	ggsave(file=path , plot=pData.tftPlot, dpi=100)
	
	path = paste(prefix, "Peer_Count.png", sep="_")
	ggsave(file=path , plot=pData.connPlot, dpi=100)
	
	path = paste(prefix, "uploadRatio.png", sep="_")
	ggsave(file=path, plot = pData.upload, dpi=100)
	
	path = paste(prefix, "uploadRatioSeeder.png", sep="_")
	ggsave(file=path, plot = pData.seederupload, dpi=100)
	
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
	
	path = paste(prefix, "NeighbourHoodSize.png", sep="_")
	ggsave(file=path, plot=pData.NeighbourHoodSize, dpi=100)
	
	path = paste(prefix, "TFTUploadRate.png", sep="_")
	ggsave(file=path, plot=pData.TFTUploadRate, dpi=100)
	
	path = paste(prefix, "OUUploadRate.png", sep="_")
	ggsave(file=path, plot=pData.OUUploadRate, dpi=100)
	
	path = paste(prefix, "TFTDownloadRate.png", sep="_")
	ggsave(file=path, plot=pData.TFTDownloadRate, dpi=100)
	
	path = paste(prefix, "OUDownloadRate.png", sep="_")
	ggsave(file=path, plot=pData.OUDownloadRate, dpi=100)
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
	

	writeLines( "Processing data ..." )
	#Do processing and generate Plots
	l = proccessData(data)
	pData = l$data
	lowerLimit = l$ll
	upperLimit = l$ul
	createPlots(pData, lowerLimit, upperLimit)
	
	writeLines( "Creating summary ..." )
	summary = DownloadTime(data, prefix)
	
	#Save the processed data into the summary file
	write.table(summary, file=histFile, sep=";", append=TRUE, col.names=FALSE, row.names = FALSE)
	
	writeLines( "Finished!" )
	
	
}