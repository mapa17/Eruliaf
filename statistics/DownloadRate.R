library(ggplot2)

#Load data
data = read.csv("DownloadRate.csv", comment.char='#', sep=';', header=F )

#Name data
# <Tick> <peer Type> <id> <MaxUpload> <MaxDownload> <CurrentUpload> <CurrentDownload>\n"
colnames(data)[1] <- "tick"
colnames(data)[2] <- "type"
colnames(data)[3] <- "pid"
colnames(data)[4] <- "maxUpload"
colnames(data)[5] <- "maxDownload"
colnames(data)[6] <- "Upload"
colnames(data)[7] <- "Download"

#Calculate averages ( be ware, depends on nPeers to never be zero!)
data$upRatio <- data$Upload / data$maxUpload
data$downRatio  <- data$Download / data$maxDownload

ggplot(data, aes(x=tick, colour=type)) + xlab("Time [ticks]") + ylab("Ratio") + geom_density(aes(y=maxUpload)) + opts(title="Upload/Download Utilization") + scale_colour_hue( name="Peers", breaks=c("peer", "peer_C1"), labels=c("BT","BT_ext") )

#tft = ggplot(data, aes(x=tick) ) + geom_line(aes(y=avgTFT, colour=type) ) + xlab("Ticks") + ylab("TFT Slots") + opts(title="Average number of TFT Slots") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )

#ou = ggplot(data, aes(x=tick) ) + geom_line(aes(y=avgOU, colour=type) ) + xlab("Ticks") + ylab("OU Slots") + opts(title="Average number of OU Slots") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )

#multiplot(tft, ou, cols=1)

#ou
#Save image to disk
#ggsave(file="Conn_OU.png" , dpi=100)

#tft
#ggsave(file="Conn_TFT.png" , dpi=100)

maxTick = max(data$tick)
#pData <- matrix(0, nrow=maxTick, ncol=3, byrow=FALSE)
#colnames(pData) <- c("Tick", "UpRatio", "DownRatio" )
tick <- 0:(maxTick*2-1)
upRate <- 1:(maxTick*2)
downRate <- 1:(maxTick*2)
type <- 1:(maxTick*2)
for(i in 0:(maxTick-1)){
	
	tick[i*2 + 1] <- i
	type[i*2 +1] <- "Peer"
	downRate[i*2 +1] <- mean( data[ (data$tick == i) & (data$type=="Peer") ,]$Download/data[(data$tick == i) & (data$type=="Peer"),]$maxDownloa )
	upRate[i*2 +1] <- mean( data[ (data$tick == i) & (data$type=="Peer") ,]$Upload/data[(data$tick == i) & (data$type=="Peer"),]$maxUpload )
	
	tick[i*2+1 + 1] <- i
	type[i*2+1 + 1] <- "Peer_C1"
	downRate[i*2+1 + 1] <- mean( data[ (data$tick == i) & (data$type=="Peer_C1") ,]$Download/data[(data$tick == i) & (data$type=="Peer_C1"),]$maxDownloa )
	upRate[i*2+1 + 1] <- mean( data[ (data$tick == i) & (data$type=="Peer_C1") ,]$Upload/data[(data$tick == i) & (data$type=="Peer_C1"),]$maxUpload )

}
pData <- data.frame(tick, type, upRate, downRate )

upload = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=upRate, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="Upload usage") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )

download = ggplot(pData, aes(x=tick) ) + geom_line(aes(y=downRate, colour=type) ) + xlab("Ticks") + ylab("Ratio") + opts(title="Download usage") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )

upload
ggsave(file="uploadRatio.png" , dpi=100)

download
ggsave(file="downloadRatio.png" , dpi=100)

