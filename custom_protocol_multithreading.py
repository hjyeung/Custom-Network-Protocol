import socket
import time
import threading
import math
from joblib import Parallel, delayed

print("\nWARNING: EXPERIMENTAL CUSTOM PROTOCOL - MAY BE UNSTABLE ON MACHINE.\nCONSIDER RUNNING THE ORIGINAL custom_protocol.py FILE INSTEAD.")

# total packet size
PACKET_SIZE = 1024
# bytes reserved for sequence id
SEQ_ID_SIZE = 4
# bytes available for message
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE

def send_closing_message(seq_id):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(("0.0.0.0", 5000))
        udp_socket.settimeout(0.5)

        finalMessage = int.to_bytes(seq_id + MESSAGE_SIZE, SEQ_ID_SIZE, byteorder='big', signed=True)
        udp_socket.sendto(finalMessage, ('localhost', 5001))

        closingMessage = int.to_bytes(-1, SEQ_ID_SIZE, byteorder='big', signed=True) + b"==FINACK=="
        udp_socket.sendto(closingMessage, ('localhost', 5001))    

# read data
def send(packet, startTime):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:

        # bind the socket to a OS port
        if (startTime == 0):
            udp_socket.bind(("0.0.0.0", threading.get_native_id()))
            udp_socket.settimeout(0.5)
            per_packet_delay = time.time()
        else:
            per_packet_delay = startTime
        
        # start sending data from 0th sequence
        seq_id = packet * MESSAGE_SIZE

        #print(packet)
        math.ceil(len(data) / MESSAGE_SIZE)

        # construct messages
        # sequence id of length SEQ_ID_SIZE + message of remaining PACKET_SIZE - SEQ_ID_SIZE bytes
        message = int.to_bytes(seq_id, SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id : seq_id + MESSAGE_SIZE]

        udp_socket.sendto(message, ('localhost', 5001))

        try:
            ack, _ = udp_socket.recvfrom(PACKET_SIZE)
            per_packet_delay = time.time() - per_packet_delay
            ack_id = int.from_bytes(ack[:SEQ_ID_SIZE], byteorder='big')
            print("Received", ack_id / 1020, "byte packet")
        except:
            print("Packet rejected")
            per_packet_delay = send(packet, per_packet_delay)
        
        return per_packet_delay

with open('file.mp3', 'rb') as f:
    data = f.read()
    data += (b'\x00' * (MESSAGE_SIZE - (len(data) % MESSAGE_SIZE)))

StartThroughputTime = time.time()
total_data = math.ceil(len(data) / MESSAGE_SIZE)
results = Parallel(n_jobs=20)(delayed(send)(i, 0) for i in range(total_data))

send_closing_message(math.ceil(len(data) / MESSAGE_SIZE))

StartThroughputTime = time.time() - StartThroughputTime
sum = 0
for i in results:
    sum += i

throughput = len(data)/StartThroughputTime
print('Throughput: {:.2f} bits / second'.format(round(throughput, 2)))
print('Average per packet delay: {:.2f} seconds'.format(round((sum / len(results)), 2)))
print('Performance metric: {:.2f}'.format(round(throughput/ (sum / len(results)), 2)))