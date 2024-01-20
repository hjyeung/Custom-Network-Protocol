# Custom TCP Protocols
A custom congestion control algorithm that maximizes throughput and minimizes per packet delay. Other TCP network protocols have been implemented to allow for performance comparisons.

## Running the network protocols
### Installation
- You will need to install [Docker](https://docs.docker.com/engine/install/ubuntu/) and Python 3.10

### Instructions
1. Navigate to the Docker folder and run ```./start-simulator.sh```
2. Run the associated network protocol Python file, such as ```sender_custom.py```

## Description of protocols
### Stop and Wait protocol
In our stop-and-wait protocol, we send out one packet and wait for an acknowledgement. Once the acknowledgement for the packet is received, the next packet in the sequence is sent. Only one packet is transmitted at any time and we incorporated a 0.5 second timeout to reduce average packet delays in the case that an acknowledgement isn’t received in time.

### Fixed Sliding window protocol
Our fixed sliding window protocol sends out 100 packets at a time and waits for the corresponding acknowledgements from the receiver. Once the sender receives these acknowledgements, our window slides and sends out the next packets in the sequence. Compared to our stop-and-wait protocol, we are able to improve bandwidth utilization as multiple packets can be transmitted at any given time.

### TCP Tahoe
Our TCP Tahoe implementation borrows elements from the sliding window protocol. During the slow start phase, the window size increases exponentially until the SSThreshold of 64 is reached. Once it is passed, we increase the window size linearly for congestion avoidance. In the case of packet loss or timeout, we re-enter the slow start phase and set the SSThreshold to ½ * window size and the window size to 1.

### TCP Reno
Our TCP Reno implementation shares similarities with TCP Tahoe, including sending out packets using a sliding window of increasing size. However, for a fast retransmit after 3 duplicate packets are received, we set the window size to SSThreshold + 3 to account for the 3 duplicate packets received.

### Custom TCP Protocol
Our custom protocol combines the higher throughput of TCP Reno with the lower average packet delay of the Stop and Wait protocol. Instead of only resetting the window size during a fast retransmit or timeout, it is also reset when the delay for a received packet is larger than a specified value. This value is determined when the program is run, by sending the first 10 packets using the Stop and Wait protocol and returning the maximimum delay multipled by 1.25. This method ensures the average packet delay will always be less than the specified maximimum value while simultaneously allowing us to achieve a ~6x throughput improvement than if the regular Stop and Wait protocol was used.

## Performance analysis
| Protocol             | Average Throughput      | Average Packet Delay | Performance Metric |
| -------------------- | ----------------------- | -------------------- | ------------------ |
| Stop and Wait        | 9,709.44 bits / second  | 0.10 seconds         | 97,094.4           |
| Fixed Sliding Window | 85,292.01 bits / second | 1.18 seconds         | 72,281.36          |
| TCP Tahoe            | 69,051.64 bits / second | 0.59 seconds         | 117,036.68         |
| TCP Reno             | 81,582.78 bits / second | 0.62 seconds         | 131,585.13         |
| Custom TCP           | 63,412.07 bits / second | 0.18 seconds         | 352,289.28         |