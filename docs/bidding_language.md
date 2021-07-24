# Bidding language
Each bidder can submit one or more bids.  A bid has two components.
- A _value_, which is the maximum amount of money the bidder is willing to 
pay (positive values) or minimum amount they are willing to accept (negative values) if the bid transacts.
- A _quantity_, which is a vector specifying the amounts of each good that 
is supplied (positive values) or demanded (negative values).
  
For example, an offer to sell 6 apples for £2 would have a value of -2 and a quantity 
+6 apples.  An offer to buy 1 apple and 2 bananas for £0.75 would have a value of 0.75 and 
a quantity of -1 apple and -2 bananas.  Positive numbers indicate giving money or goods and 
negative numbers indicate taking.

## Divisibility
By default, bids are treated as indivisible.  This means that if the bid to sell 6 apples 
transacts, then all six apples are sold.  Optionally, bids can be 
set as divisible.  This would allow, say, two of the six apples (or even just a slice of 
apple) to be sold.

## XOR Bids
When a bidder submits multiple bids, some of the bids can be mutually exclusive (XOR bids) 
and some can be independent (OR bids).  For example, suppose a bidder would like a 
snack of either an apple or a banana but not both.  They would submit two bids with the same
 "XOR group".  This adds the restriction that at most one of the two bids can transact. 

##  Labels
The bidding language allows a _label_ to be attached to each bid.  The label does not 
affect the outcome of the market.  Its sole purpose to aid interpretation of the results.