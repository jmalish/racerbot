# Imports
import socket
import time

# Some basic variables used to configure the bot
server = "irc.freenode.net"
port = 6667
channel = "#racerbottestroom"  # test room, uncomment next line to overwrite this channel and use 'real' channel
# channel = "#hoggit.iracing"  # actual channel, uncomment this line when ready to join
botnick = "racerbot_py"
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# <editor-fold desc="Basic Functions">
# joins channels
def joinchan(chan):
    ircsock.send("JOIN " + chan +"\n")
    print "Joining " + chan

# responds to pings from server
def ping():
    ircsock.send("PONG :Pong\n")
    print "PONG!"

# funtion to send message, a little easier than typing ircsocket over and over
def sendMsg(message):
    now = time.strftime("%I:%M:%S")
    ircsock.send('PRIVMSG %s: %s\r\n' % (channel, message))
    print "%s: I sent: %s" % (now, message)
# </editor-fold desc="Basic Functions">

# </editor-fold desc="Commands">
def commands(nick, channel, message):
    if message.find(".here") != -1:  # checks if bot is listening to us
        sendMsg("Yup!")
# </editor-fold desc="Commands">


# <editor-fold desc="Bot">
# setting up socket
ircsock.connect((server, port))  # Here we connect to the server using port 6667
ircsock.send("USER " + botnick + " " + botnick + " " + botnick + " Created by racer0940\n")  # user authentication
print "Authenticating"
ircsock.send("NICK " + botnick + "\n")  # here we actually assign the nick to the bot
print "Assigning name"

joinchan(channel)  # initial channel join

while True:  # this is the actual bot itself, everything in this block is what the bot uses
    ircmsg = ircsock.recv(2048)  # receive data from server
    ircmsg = ircmsg.strip('\n\r')  # strip any unnecessary line breaks
    now = time.strftime("%I:%M:%S")
    print(now + " - " + ircmsg)  # print message to console

    if ircmsg.find("PING :") != -1:  # don't want to be rude, respond to servers pings
        ping()

    if ircmsg.find(' PRIVMSG '):
        nick = ircmsg.split('!')[0][1:]
        channel = ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
        message = ircmsg.split(' :')[-1]

        commands(nick, channel, message)
# </editor-fold desc="Bot">

# example message in channel (what shows up in the console):
# :racer0940!sid15960@gateway/web/irccloud.com/x-gigiyhibuoxitvuf PRIVMSG #racerbottestroom :test

# example of PM to bot
# :racer0940!sid15960@gateway/web/irccloud.com/x-gigiyhibuoxitvuf PRIVMSG racerbot_py :test
