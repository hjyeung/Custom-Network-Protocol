import socket
from datetime import datetime
import time

# total packet size
PACKET_SIZE = 1024
# bytes reserved for sequence id
SEQ_ID_SIZE = 4
# bytes available for message
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE
# total packets to send
WINDOW_SIZE = 1
SSTHRESH = 64

# read data
with open('file.mp3', 'rb') as f:
    data = f.read()
    data += (b'\x00' * (MESSAGE_SIZE - (len(data) % MESSAGE_SIZE)))

# send next message for the sliding window
def send_message(seq_id):
    global per_packet_delay

    temp_id = seq_id
    if (seq_id < len(data)):
        #print("SENT", temp_id / 1020)
        message = int.to_bytes(temp_id, SEQ_ID_SIZE, byteorder='big', signed=True) + data[temp_id : temp_id + MESSAGE_SIZE]
        per_packet_delay[temp_id] = time.time()
        udp_socket.sendto(message, ('localhost', 5001))
    return (seq_id + MESSAGE_SIZE)

# resend message at seq_id
def resend_message(seq_id):
    message = int.to_bytes(seq_id, SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id : seq_id + MESSAGE_SIZE]
    udp_socket.sendto(message, ('localhost', 5001))
    print("Resend", (seq_id / 1020).__str__(), "byte packet")

def send_closing_message(seq_id):
    finalMessage = int.to_bytes(seq_id + MESSAGE_SIZE, SEQ_ID_SIZE, byteorder='big', signed=True)
    udp_socket.sendto(finalMessage, ('localhost', 5001))

    closingMessage = int.to_bytes(-1, SEQ_ID_SIZE, byteorder='big', signed=True) + b"==FINACK=="
    udp_socket.sendto(closingMessage, ('localhost', 5001))    

def reset_window_size():
    global SSTHRESH, WINDOW_SIZE
    SSTHRESH = int(WINDOW_SIZE/2)
    WINDOW_SIZE = 1

def kinda_reset_window_size():
    global SSTHRESH, WINDOW_SIZE
    SSTHRESH = int(WINDOW_SIZE/2)
    WINDOW_SIZE = SSTHRESH + 3

def send_window_size(seq_id):
    global WINDOW_SIZE

    temp_id = seq_id
    for i in range(WINDOW_SIZE):
        temp_id = send_message(temp_id)

    return temp_id
        
# create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:

    # bind the socket to a OS port
    udp_socket.bind(("0.0.0.0", 5000))
    udp_socket.settimeout(0.1)
    
    # start sending data from 0th sequence
    seq_id = 0
    max_seq_id = 0
    temp_window_size_adder = 0.0
    StartThroughputTime = time.time()
    fast_retransmit = 0

    acks_num = 0
    per_packet_delay = {}

    max_seq_id = send_window_size(seq_id)
    while seq_id < len(data):        
        try:
            # wait for ack
            ack, _ = udp_socket.recvfrom(PACKET_SIZE)
            
            # extract ack id
            ack_id = int.from_bytes(ack[:SEQ_ID_SIZE], byteorder='big')
            print("Received", ack_id / 1020, "byte packet")

            acks_num += 1
            
            if (ack_id == seq_id):
                fast_retransmit += 1
                if (fast_retransmit == 2): # 3 duplicate acks received
                    print("Fast retransmit due to 3 duplicate acknowledgements")
                    kinda_reset_window_size()
                    fast_retransmit = 0
                    resend_message(seq_id)
                elif (seq_id + MESSAGE_SIZE > len(data)):
                    break
            elif (ack_id != seq_id):
                fast_retransmit = 0
                while (seq_id < ack_id):
                    per_packet_delay[seq_id] = time.time() - per_packet_delay[seq_id]
                    seq_id += MESSAGE_SIZE

            if (seq_id == max_seq_id):
                if (WINDOW_SIZE < SSTHRESH):
                    fast_retransmit = 0
                    WINDOW_SIZE *= 2
                    max_seq_id = send_window_size(seq_id)
                else:
                    fast_retransmit = 0
                    WINDOW_SIZE += 10
                    max_seq_id = send_window_size(seq_id)

        except socket.timeout:
            # no acknowledgement received, resend unacked message
            fast_retransmit = 0
            print("Socket timeout")
            reset_window_size()
            resend_message(seq_id)
        if (seq_id + MESSAGE_SIZE >= len(data)):
            break

    # send final closing message
    send_closing_message(seq_id)

    totalTime = (time.time() - StartThroughputTime)
    totalPackages = int(len(data)/MESSAGE_SIZE) + (len(data) % MESSAGE_SIZE > 0)

    per_packet_delay.popitem()
    total = 0.0
    count = 0
    for value in per_packet_delay.values():
        total += value
        count += 1

    print('\nThroughput: {:.2f} bits / second'.format(round(len(data) / totalTime, 2)))
    print('Average per packet delay: {:.2f} seconds'.format(round(total / count, 2)))
    print('Performance metric: {:.2f}'.format(round((len(data) / totalTime) / (total / count), 2)))