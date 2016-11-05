Corresponding to revision on [CPU share definition ](cpu_share.md), we will further revise our definition of a capacity function.

## Tentative Model

We define a capacity function on a PM a function such that

 * Domain is on [0, `min(NCores * 100, saturation_point)`] where `saturation_point` is the CPU usage at which packets start to drop.
 * Range is on R+.

To measure capacity function, we use the following mechanism:

**TBD**.

## Regression

Actually we don't need to convert the raw values to a regression function... We can use the values directly...

## Questions

What if we later take link delay into consideration? Will the new scheme adapt?


