#peerD = read.csv("dt_peer.csv", comment.char='#', sep=';', header=F )
#peer = hist(peerD$V3-peerD$V2, plot=F)
#peer_C1D = read.csv("dt_peer_c1.csv", comment.char='#', sep=';', header=F )
#peer_C1 = hist(peer_C1D$V3-peer_C1D$V2, plot=F)
#
#barplot(peer$counts, names.arg=peer$mids)

#Load the ggplot functions
library(ggplot2)


peerD = read.csv("dt_peer.csv", comment.char='#', sep=';', header=F )
peer_C1D = read.csv("dt_peer_c1.csv", comment.char='#', sep=';', header=F )

#Transform the input vector to a table containing a colum time and a colum type
peer = data.frame( time = peerD$V3 - peerD$V2 )
peer$type <- 'peer'
peerC1 = data.frame( time = peer_C1D$V3 - peer_C1D$V2 )
peerC1$type <- 'peer_C1'

#Fuse the two tables to one
comb <- rbind(peer,peerC1)

#qplot(time, data=comb, fill=type, geom="density", alpha="0.4" , xlab="Download time [ticks]" , ylab="Peers [ration]" )
#ggplot(comb, aes(x=time, fill=type)) + xlab("Download time [ticks]") + ylab("Peers [ratio]") + geom_density(alpha=0.4)
#ggplot(comb, aes(x=time, colour=type)) + xlab("Download time [ticks]") + ylab("Peers [ratio]") + geom_density()

ou = ggplot(data, aes(x=tick) ) + geom_line(aes(y=avgOU, colour=type) ) + xlab("Ticks") + ylab("OU Slots") + opts(title="Average number of OU Slots") + scale_color_manual( name="Peers", breaks=c("Peer", "Peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )

ggplot(comb, aes(x=time, fill=type)) + xlab("Download time [ticks]") + ylab("Peers") + geom_histogram(position=position_dodge()) + opts(title="Download time") + scale_fill_hue( name="Peers", breaks=c("peer", "peer_C1"), labels=c("BT","BT_ext") )
ggsave(file="downloadTime_hist.png" , dpi=100)

ggplot(comb, aes(x=time, colour=type)) + xlab("Download time [ticks]") + ylab("Peers [ratio]") + geom_density() + opts(title="Download time") + scale_colour_hue( name="Peers", breaks=c("peer", "peer_C1"), labels=c("BT","BT_ext") )
ggsave(file="downloadTime_den.png" , dpi=100)

