library(ggplot2)

peerD = read.csv("peerCnt.csv", comment.char='#', sep=';', header=F )
peer_C1D = read.csv("peerCntC1.csv", comment.char='#', sep=';', header=F )

colnames(peerD)[1] <- "tick"
colnames(peerD)[2] <- "peer"
colnames(peerD)[3] <- "completed"

colnames(peer_C1D)[1] <- "tick"
colnames(peer_C1D)[2] <- "peer"
colnames(peer_C1D)[3] <- "completed"


#Extract data about total peer count on peer and peer_C1
t <- data.frame( tick = peerD$tick , type="peer", peers=peerD$peer )
t1 <- data.frame( tick = peer_C1D$tick , type="peer_C1", peers=peer_C1D$peer )
t3 = rbind(t,t1)

#This would print only the total peer number as area plot
#ggplot(t3, aes(x=t3$tick) ) + geom_area(aes(y=peers, fill=type) , alpha=0.4)


#Do the same like before but for the completed peers
tt <- data.frame( tick = peerD$tick , type="peer", peers=peerD$completed )
tt1  <- data.frame( tick = peer_C1D$tick , type="peer_C1", peers=peer_C1D$completed )
tt3 = rbind(tt,tt1)

ggplot(t3, aes(x=t3$tick) ) + geom_area(aes(y=peers, fill=type) , alpha=0.4 , position=position_identity() ) + geom_line( aes(y=tt3$peers, colour=type) ,position=position_identity()) + ylab("Peers") + xlab("Ticks") + opts(title="Total and completed Peers") + scale_fill_manual( name="Total Peers", breaks=c("peer", "peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") ) + scale_color_manual( name="Completed Peers", breaks=c("peer", "peer_C1"), labels=c("BT","BT_ext") , values=c("red", "blue") )

#Save image to disk
ggsave(file="peerCnt.png" , dpi=100)
