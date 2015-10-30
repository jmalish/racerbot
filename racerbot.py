# Import some necessary libraries.
import socket

# Some basic variables used to configure the bot
server = "irc.freenode.net"
port = 6667
channel = "#racerbottestroom"  # test room, uncomment next line to overwrite this channel and use 'real' channel
# channel = "#hoggit.iracing"  # actual channel, uncomment this line when ready to join
botnick = "racerbot_py"
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# <editor-fold desc="Functions">
# basic function to send messages to server
def sendmsg(chan, msg):
    ircsock.send("PRIVMSG " + chan + " :" + msg +"\n")

# joins channels
def joinchan(chan):
    ircsock.send("JOIN " + chan +"\n")

# responds to pings from server
def ping():
    ircsock.send("PONG :Pong\n")
# </editor-fold desc="Functions">


# <editor-fold desc="Bot">
# setting up socket
ircsock.connect((server, 6667))  # Here we connect to the server using port 6667
ircsock.send("USER " + botnick + " " + botnick + " " + botnick + " Created by racer0940\n")  # user authentication
ircsock.send("NICK " + botnick + "\n")  # here we actually assign the nick to the bot

joinchan(channel)  # initial channel join

while True:  # this is the actual bot itself, everything in this block is what the bot uses
    ircmsg = ircsock.recv(2048)  # receive data from server
    ircmsg = ircmsg.strip('\n\r')  # strip any unnecessary line breaks
    print(ircmsg)  # print message to console


# </editor-fold desc="Bot">

# example message (what shows up in the console):
# :racer0940!sid15960@gateway/web/irccloud.com/x-gigiyhibuoxitvuf PRIVMSG #racerbottestroom :test
