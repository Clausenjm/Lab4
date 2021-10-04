"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 0NN
- Fall 202N
- Lab 4 receive messages
- Names:
  - Josiah Clausen
  - Elisha Hamp

A simple TCP server/client pair.

The application protocol is a simple format: For each file uploaded, the client first sends four (big-endian) bytes indicating the number of lines as an unsigned binary number.

The client then sends each of the lines, terminated only by '\\n' (an ASCII LF byte).

The server responds with 'A' when it accepts the file.

Then the client can send the next file.


Introduction: (Describe the lab in your own words)




Summary: (Summarize your experience with the lab, what you learned, what you liked, what you disliked, and any suggestions you have for improvement)




"""

# import the 'socket' module -- not using 'from socket import *' in order to selectively use items with 'socket.' prefix
import socket
import struct
import time
import sys

# Port number definitions
# (May have to be adjusted if they collide with ports in use by other programs/services.)
TCP_PORT = 12100

# Address to listen on when acting as server.
# The address '' means accept any connection for our 'receive' port from any network interface
# on this system (including 'localhost' loopback connection).
LISTEN_ON_INTERFACE = ''

# Address of the 'other' ('server') host that should be connected to for 'send' operations.
# When connecting on one system, use 'localhost'
# When 'sending' to another system, use its IP address (or DNS name if it has one)
# OTHER_HOST = '155.92.x.x'
OTHER_HOST = 'localhost'


def main():
    """
    Allows user to either send or receive bytes
    """
    # Get chosen operation from the user.
    action = input('Select "(1-TS) tcpsend", or "(2-TR) tcpreceive":')
    # Execute the chosen operation.
    if action in ['1', 'TS', 'ts', 'tcpsend']:
        tcp_send(OTHER_HOST, TCP_PORT)
    elif action in ['2', 'TR', 'tr', 'tcpreceive']:
        tcp_receive(TCP_PORT)
    else:
        print('Unknown action: "{0}"'.format(action))


def tcp_send(server_host, server_port):
    """
    - Send multiple messages over a TCP connection to a designated host/port
    - Receive a one-character response from the 'server'
    - Print the received response
    - Close the socket
    
    :param str server_host: name of the server host machine
    :param int server_port: port number on server to send to
    """
    print('tcp_send: dst_host="{0}", dst_port={1}'.format(server_host, server_port))
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((server_host, server_port))

    num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    while num_lines != 0:
        print('Now enter all the lines of your message')
        # This client code does not completely conform to the specification.
        #
        # In it, I only pack one byte of the range, limiting the number of lines this
        # client can send.
        #
        # While writing tcp_receive, you will need to use a different approach to unpack to meet the specification.
        #
        # Feel free to upgrade this code to handle a higher number of lines, too.
        tcp_socket.sendall(b'\x00\x00')
        time.sleep(1)  # Just to mess with your servers. :-)
        tcp_socket.sendall(b'\x00' + bytes((num_lines,)))

        # Enter the lines of the message. Each line will be sent as it is entered.
        for line_num in range(0, num_lines):
            line = input('')
            tcp_socket.sendall(line.encode() + b'\n')

        print('Done sending. Awaiting reply.')
        response = tcp_socket.recv(1)
        if response == b'A':  # Note: == in Python is like .equals in Java
            print('File accepted.')
        else:
            print('Unexpected response:', response)

        num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    tcp_socket.sendall(b'\x00\x00')
    time.sleep(1)  # Just to mess with your servers. :-)  Your code should work with this line here.
    tcp_socket.sendall(b'\x00\x00')
    response = tcp_socket.recv(1)
    if response == b'Q':  # Reminder: == in Python is like .equals in Java
        print('Server closing connection, as expected.')
    else:
        print('Unexpected response:', response)

    tcp_socket.close()


def tcp_receive(listen_port):
    """
    - programed by Josiah Clausen
    - Listen for a TCP connection on a designated "listening" port
    - Accept the connection, creating a connection socket
    - Print the address and port of the sender
    - Repeat until a zero-length message is received:
      - Receive a message, saving it to a text-file (1.txt for first file, 2.txt for second file, etc.)
      - Send a single-character response 'A' to indicate that the upload was accepted.
    - Send a 'Q' to indicate a zero-length message was received.
    - Close data connection.

    :param int listen_port: Port number on the server to listen on
    """

    print('tcp_receive (server): listen_port={0}'.format(listen_port))
    # Replace this comment with your code.
    message_number = 1
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('', listen_port))
    listen_socket.listen(1)
    data_socket, sender_address = listen_socket.accept()

    while listen_socket:
        listen_socket = read_messages(data_socket, message_number)

    data_socket.close()


def read_messages(data_socket, message_number):
    """
    -programed by Josiah Clausen
    - gets the first 4 bytes of the data socket and reads how many lines the file contains
    -:param Socket data_socket: the data socket that will be used to access the bytes and read the
    -:param int message_number: the number of the message being sent to keep track of what file it is saved to
    """
    var_return = True
    if read_message(data_socket, message_number):
        data_socket.send(b'A')
        message_number += 1
    else:
        data_socket.send(b'Q')
        var_return = False

    return var_return


# Add more methods here (Delete this line)
def read_message(data_socket, number):
    """
        - reads the 4 byte header
        -:param Socket data_socket: the data socket that will be used to access the bytes and read the
        -:param int number: this number is used to increment the value of the file name so each message is saved
        - to a different file
    """
    is_not_empty = False
    try:
        length = read_header(data_socket)

        is_not_empty = True
        if length != 0:
            write_to_text_file(read_line(length, data_socket), number)
        else:
            is_not_empty = False
    except OSError:
        print('messages have ended')
    return is_not_empty


def read_header(data_socket):
    """
    - gets the first 4 bytes of the data socket and reads how many lines the file contains
    -:param Socket data_socket: the data socket that will be used to access the bytes and read the
    """
    if data_socket != 0:
        b_list = [next_byte(data_socket), next_byte(data_socket), next_byte(data_socket), next_byte(data_socket)]
        header = b_list.pop() + b_list.pop() + b_list.pop() + b_list.pop()
        header = int.from_bytes(header, 'little')
        print(header)

    return header


def read_line(line_amount, data_socket):
    """
    - creates lines of text character by character
    -:param String line_amount: gets an int for the amount of lines that are in the text file
    -:param Socket data_socket: the data socket is used to retrieve the rest of the message after the header has been read
    """
    line = ''
    for i in range(0, line_amount):

        char = next_byte(data_socket).decode()
        while char != '\n':
            line = line + char
            char = next_byte(data_socket).decode()

        line += '\r\n'

    print(line)
    return line


def write_to_text_file(text_block, message_num):
    """
    - programed by Josiah Clausen
    - takes in a text block and the message number to write to a file and create one
    - the text block is converted to to bytes and writen to a byte file
    - a new text file is writen with increasing value such as 1.txt, 2.txt... and so on
    - if the server is restarted old files will be over written
    -:param String text_block: gets the text from the server in string form and writes it to a bytes file
    -:param int message_num: keeps track of the message being sent from 1, 2, 3..... etc is and int
    """
    output_file = open(str(message_num) + '.txt', "wb")
    output_file.write(text_block.encode('ASCII') + b'\r\n')


def next_byte(data_socket):
    """
    Read the next byte from the socket data_socket.
   
    Read the next byte from the sender, received over the network.
    If the byte has not yet arrived, this method blocks (waits)
      until the byte arrives.
    If the sender is done sending and is waiting for your response, this method blocks indefinitely.
   
    :param data_socket: The socket to read from. The data_socket argument should be an open tcp
                        data connection (either a client socket or a server data socket), not a tcp
                        server's listening socket.
    :return: the next byte, as a bytes object with a single byte in it
    """

    return data_socket.recv(1)


# Invoke the main method to run the program.
main()
