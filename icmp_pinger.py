# import
from socket import *
import os
import sys
import struct
import time
import select
import binascii
import socket

# The request type
ICMP_ECHO_REQUEST = 8
roundTripTimeLog = []
sent = 0
received = 0

# the checksum for the packet header
def checksum(string):
    val = 0
    stop = (len(string) / 2) * 2
    count = 0
    while count < stop:
        temp = ord(string[count+1]) * 256 + ord(string[count])
        val = val + temp
        val = val & 0xffffffffL
        count = count + 2
    if stop < len(string):
        val = val + ord(string[len(string) - 1])
        val = val & 0xffffffffL
        val = (val >> 16) + (val & 0xffff)
        val = val + (val >> 16)
    result = ~val
    result = result & 0xffff
    result = result >> 8 | (result << 8 & 0xff00)
    return result

# receive a a single ping from an end system
# will be called when the ping function is
# called
def receivePing(mySocket, myID, timeout, destination):
    global received
    global roundTripTimeLog
    timeRemaining = timeout
    while 1:
        # the time it started the process
        streamStarted = time.time()
        # provides access to the select() and poll()
        # functions available in most operating systems
        stream = select.select([mySocket], [], [], timeRemaining)
        # create an object of the stream
        streamDuration = (time.time() - streamStarted)
        print stream
        # check if the channel is empty
        if stream[0] == []:
            return "0: Destination Network Unreachable"
        receivedAt = time.time()
        # receive data from the specified port
        # the return pair is (string, address)
        # where string is the packet received and
        # and the address of the socket
        packet, addr = mySocket.recvfrom(1024)
        # the header from the packet, which are
        # bytes 20 - 28 of the first 160 bits
        header = packet[20:28]
        # the header comes in as bytes and needs to be converted
        # into decimal
        # here by specifying 2 unsigned integers,
        # 2 integers and 1 short into a struct
        # the bytes can be read
        unpacked_requestType, unpacked_code, unpacked_checksum, unpacked_id, unpacked_sequence = struct.unpack("bbHHh", header)
        if myID == unpacked_id:
            bytes = struct.calcsize('d')
            # get the sequence value which is returned
            # in the echo reply
            sequenceValue = struct.unpack('d',recPacket[28:28 + bytes])[0]
            # add it to the log
            totalTime = receivedAt - sequenceValue
            roundTripTimeLog.append(totalTime)
            received += 1
            return totalTime
        else:
            # the ids don't match
            return "0: IP Header Bad"
        # reset the time
        timeRemaining = timeRemaining - streamDuration
        if timeRemaining <= 0:
            return "1: Destination Host Unreachable"

# send a single ping to an end system
def sendPing(mySocket, destination, myID):
    global sent
    # the header is
    # type 8 bits
    # code is 8 bits
    # checksum is 16 bits
    # id is 16 bits
    # squence is 16 bits
    defaultChecksum = 0
    # make a header to send over to the
    # end system with a 0 checksum
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, defaultChecksum, myID, 1)
    data = struct.pack('d', time.time())
    # get the checksum
    defaultChecksum = checksum(header + data)
    # handle the darwin platform
    if sys.platform == 'darwin':
        # convert 16-bit integers from host to network
        defaultChecksum = socket.htons(defaultChecksum) & 0xffff
    else:
        # get from host to network
        defaultChecksum = socket.htons(defaultChecksum)

        # recreate the header
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, defaultChecksum, myID, 1)
    packet = header + data
    mySocket.sendto(packet, (destination, 1))
    # sent 1
    sent += 1

# will return the time it takes to perform
# a sent ping to an address
# to receive a ping at an address
def ping(destination, timeout):
    # create the new socket
    # af_net is the proper address family to handle the
    # ipv4 protocol
    # handle possible exceptions
    try:
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    except socket.error, (errno, message):
        if errno == 1:
            # the socket failed to be created
            # with the given destination
            # the current process is most operating systems
            # have icmp pings built in to their processes
            raise socket.error(message)
    device = os.getpid() & 0xFFFF
    sendPing(mySocket, destination, device)
    timeToReceive = receivePing(mySocket, device, timeout, destination)
    # close the socket
    mySocket.close()
    return timeToReceive

def continuousPing(host, timeout = 1):
    # the timeout period is 1
    # then drop the connection
    destination = socket.gethostbyname(host)
    print "Pining " + destination + "..."
    print ""
    # send every second
    while 1:
        timeToReceive = ping(destination, timeout)
        print "Round Trip Time: " + timeToReceive
        # wait
        time.sleep(1)
    return timeToReceive

# will retrieve all the open ports on the
# host
def getOpenPorts(host):
    # get the destination
    destination = socket.gethostbyname(host)
    try:
        # for each available port
        # that is reserved
        print "Open Ports..."
        for port in range(1, 1024):
            # make a socket
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # get the port
            val = mySocket.connect_ex((destination, port))
            # the connection was successful
            # therefore the port is open
            if val == 0:
                # format the string in a way that c
                # respects pythons operands
                print "Port {}:  is open".format(port)
            sock.close()
    except socket.error (errno, message):
        # close the connection
        print message
        sys.exit()
continuousPing("www.xavier.edu")
getOpenPorts("24.209.74.86")













