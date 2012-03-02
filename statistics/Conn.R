library(ggplot2)

#Define multiplot function
multiplot <- function(..., plotlist=NULL, cols) {
    require(grid)

    # Make a list from the ... arguments and plotlist
    plots <- c(list(...), plotlist)

    numPlots = length(plots)

    # Make the panel
    plotCols = cols                          # Number of columns of plots
    plotRows = ceiling(numPlots/plotCols) # Number of rows needed, calculated from # of cols

    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(plotRows, plotCols)))
    vplayout <- function(x, y)
        viewport(layout.pos.row = x, layout.pos.col = y)

    # Make each plot, in the correct location
    for (i in 1:numPlots) {
        curRow = ceiling(i/plotCols)
        curCol = (i-1) %% plotCols + 1
        print(plots[[i]], vp = vplayout(curRow, curCol ))
    }

}


#Load data
data = read.csv("Conn.csv", comment.char='#', sep=';', header=F )

#Name data
#<Tick> <peer Type> <Total # of max TFT Slots> <Total # of max OU Slots> <Total # of used TFT Slots> <Total # of used OU Slots> <# of peers>
colnames(data)[1] <- "tick"
colnames(data)[2] <- "type"
colnames(data)[3] <- "maxTFT"
colnames(data)[4] <- "maxOU"
colnames(data)[5] <- "TFT"
colnames(data)[6] <- "OU"
colnames(data)[7] <- "nPeers"

#Calculate averages ( be ware, depends on nPeers to never be zero!)
data$avgTFT  <- data$TFT / data$nPeers
data$avgOU  <- data$OU / data$nPeers
data$avgMaxTFT  <- data$maxTFT / data$nPeer
data$avgMaxOU  <- data$maxOU / data$nPeers

tft = ggplot(data, aes(x=tick) ) + geom_line(aes(y=avgTFT, colour=type) ) + xlab("Ticks") + ylab("TFT Slots") + opts(title="Average number of TFT Slots") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )

ou = ggplot(data, aes(x=tick) ) + geom_line(aes(y=avgOU, colour=type) ) + xlab("Ticks") + ylab("OU Slots") + opts(title="Average number of OU Slots") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )

#multiplot(tft, ou, cols=1)

ou
#Save image to disk
ggsave(file="Conn_OU.png" , dpi=100)

tft
ggsave(file="Conn_TFT.png" , dpi=100)

