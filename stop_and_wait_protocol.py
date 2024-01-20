import socket
import time

# total packet size
PACKET_SIZE = 1024
# bytes reserved for sequence id
SEQ_ID_SIZE = 4
# bytes available for message
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE

def send_closing_message(seq_id):
    finalMessage = int.to_bytes(seq_id + MESSAGE_SIZE, SEQ_ID_SIZE, byteorder='big', signed=True)
    udp_socket.sendto(finalMessage, ('localhost', 5001))

    closingMessage = int.to_bytes(-1, SEQ_ID_SIZE, byteorder='big', signed=True) + b"==FINACK=="
    udp_socket.sendto(closingMessage, ('localhost', 5001))    

# read data
with open('file.mp3', 'rb') as f:
    data = f.read()
    data += (b'\x00' * (MESSAGE_SIZE - (len(data) % MESSAGE_SIZE)))
 
# create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:

    # bind the socket to a OS port
    udp_socket.bind(("0.0.0.0", 5002))
    udp_socket.settimeout(0.5)
    
    # start sending data from 0th sequence
    seq_id = 0
    StartThroughputTime = time.time()

    per_packet_delay = {}
    while seq_id < len(data):
        
        # create messages
        seq_id_tmp = seq_id

        # construct messages
        # sequence id of length SEQ_ID_SIZE + message of remaining PACKET_SIZE - SEQ_ID_SIZE bytes
        message = int.to_bytes(seq_id_tmp, SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id_tmp : seq_id_tmp + MESSAGE_SIZE]

        udp_socket.sendto(message, ('localhost', 5001))
        per_packet_delay[seq_id] = time.time()

        try:
            ack, _ = udp_socket.recvfrom(PACKET_SIZE)
            per_packet_delay[seq_id] = time.time() - per_packet_delay[seq_id]
            ack_id = int.from_bytes(ack[:SEQ_ID_SIZE], byteorder='big')
            print("Received", ack_id / 1020, "byte packet")
        except:
            print("Packet rejected")
            udp_socket.sendto(message, ('localhost', 5001))

        seq_id += MESSAGE_SIZE
        
    # send final closing message
    send_closing_message(seq_id)

    totalTime = (time.time() - StartThroughputTime)
    totalPackages = int(len(data) / MESSAGE_SIZE) + (len(data) % MESSAGE_SIZE > 0)

    per_packet_delay.popitem()
    total = 0.0
    count = 0
    for value in per_packet_delay.values():
        total += value
        count += 1

    print('\nThroughput: {:.2f} bits / second'.format(round(len(data) / totalTime, 2)))
    print('Average per packet delay: {:.2f} seconds'.format(round(total / count, 2)))
    print('Performance metric: {:.2f}'.format(round((len(data) / totalTime) / (total / count), 2)))