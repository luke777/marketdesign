# TXT Bid format

The TXT format is the most concise format. There is one row per _bidder_.

The row begins with an optional bidder name followed by a colon, e.g. `seller 1: `.  If the name is not specified, one is automatically generated.

Then there is one or more bids.  Each bid is a space separated list of numbers.  The first entry is the amount of money offer (positive numbers) or demanded (negative numbers).  The subsequent entries are amounts of each of the goods offered or demanded.

XOR bids are separated by commas, e.g. `-10 0 1, -9 1 0` and OR bids are separated by "|", e.g. `-10 0 1 | -9 1 0`.  Divisible bids are preceded by a "d", e.g. `d -20 2 0`.  Mixed divisible bids are preceded by an "m", e.g. `m -20 2 0`.  All bids must have the same number of entries, which is equal to the number of goods being traded plus one (for money).  

The example below shows a seller independently offer an apple and a banana, and two buyers interested in the apple and banana respectively.

`seller: -5 1  0 | -7 0 1` \
`buyer A: 8 -1 0` \
`buyer B: 10 0 -1`