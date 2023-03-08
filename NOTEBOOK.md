# Engineering Notebook

### By Ashlan Ahmed, Charles Ma, and Christy Jestin

## Intro

This is the engineering notebook for the second design project in CS 262. Our assignment was to create a scale model for logical clocks. We had to run 3 separate processes that communicated with each other and updated their own logical clocks based on both their internal operations and the inter-process communication. These clocks would have potentially different clock rates (in ticks/sec) that fell into the range [1, 6]. Then we investigated the effects of increasing the probability of communication and decreasing the range of clock rates.

## Inter-process Communication

From here on out, we'll refer to the three processes as a, b, and c. The primary design decision for this assignment was handling inter-process communication. First, the three processes need peer to peer connections since there is no server to act as a go between. We did this by defining 3 ports for a <-> b, a <-> c, and b <-> c. In each case, the process with the lower letter accepted a connection from the process with the higher letter. Finally, we had each process open a pair of threads to listen for messages from the other two processes since writing to the network queue isn't limited by a clock rate. All other components of the design were more or less fully determined by the specifications.

## Average Jump

![average jump graph]()

This graph shows the average jump computed over all processes for a particular trial and setting. There are 5 trials per setting and 3 different settings. In each trial, we have a new set of 3 random clock cycles. A standard clock progression would just increase the clock by 1, so we want to compare these average jump values to 1 to understand how differing clock rates can cause bigger jumps in the logical clock progression.

It should be noted that jumps are closely related to drift in the logical clocks since the jump resolves the drift and catches the slower process up to the faster process. Thus whenever we observe bigger jumps, there will be greater drift and vice versa.

![average queue length]()

This graph shows the average length of the queue during reads from the network queue. If two processes have the same clock cycle, they should have queue lengths very close to 0 since they're reading at the same rate that the other process is sending messages. On the other hand, if one process is slower than the other, then the network queue will build up on the slower process as the faster process sends out more messages.

## Effect of Smaller Clock Cycle Range

We narrowed the clock rate range from [1, 6] to [1, 3]. As seen in the graph above, this doesn't change the variation in the average jump, but it does shift the averages down. This makes sense because if the clock cycles are closer, then synchronizations will cause smaller jumps since the slower clock cycle won't be as far behind.

We see a similar effect on the average queue length as the closer clock cycles mean that there will be less build up on a slower process's network queue. The queue length differs from the jumps since the average queue lengths are much tighter in this setting than the standard runs. This does make sense because the narrow clock cycle range also means that the distribution of clock rate differences is tighter. It's unclear why this trend doesn't hold for the average jump as well as the average length of the queue.

## Effect of Lower Internal Event Probability

Typically if the network queue is empty, then there is a 70% chance that the process will perform an internal event i.e. not send out a message to the other processes. In our experiment, we decreased the chance to 20%. As seen in the graph, this produces an average jump that is comparable to the smaller clock cycle range's effect but with much less variation since the averages are closer together. This means that the lower internal event probability both decreases the average jump and decreases the variance in average jump from trial to trial.

The first impact makes sense because a higher probability of an internal event would allow a high clock cycle process to go through more clock ticks before sending out a message and causing a lower clock cycle process to synchronize. This allows for the gap between the processes to build up as the send message happens later than if the probability of an internal event was lower. Thus lowering the probability would have the inverse effect of decreasing the average jump.

The decrease in variation also makes sense because the lower internal event probability makes it harder to go several clock ticks without synchronizing &mdash; which means that we'll see fewer large jumps. In essence, the same effect that brings down the average would also bring down the variation since distribution is just getting tighter.

On the other hand, we see that the average queue lengths get larger and have higher variance as we decrease the internal event probability. This is because the higher communication probability would cause slower processes to have even more buildup on the network queue as the faster process sends more messages.
