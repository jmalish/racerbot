channel = "#racerbot.testroom"
ircmsg = ":racer0940!sid15960@gateway/web/irccloud.com/x-lxdtditmqlusbxoi PRIVMSG #racerbot.testroom :test message and : in it"

message = ircmsg.split(' :', 1)[1]

print message

# nick = ircmsg.split("!")[0].strip(":")
# message = ircmsg.split(channel + " :")[1]
# print "%s - %s: %s" % (now, nick, message)
# print ircmsg
