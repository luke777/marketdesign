# CSV Bid format

The CSV format is convenient if bids are prepared in a spreadsheet. There is one row per _bid_.

The following columns are required.
- **name** identifies the bidder.
- **value** is the amount of money bid.  Positive values indicate giving money (i.e. buying) and negative values indicate taking money (i.e. selling).
- One column for each good being traded.  The column header is the good's name.  Entries in the column indicate the quantity being supplied (positive numbers) and demanded (negative numbers).  Blank entries are allowed to indicate zeros.

An example with three bidders and two goods is as follows.

| name | value | apples | bananas |
|------|-------|--------|---------|
|seller| -5    |    +1  |         |
|seller| -7    |        |    +1   |
|buyer A| +8    |    -1  |         |
|buyer B|  +10   |        |   -1    |

The following optional columns can be included if desired.

- **xor_group** A string identifying the xor-group or empty if no xor-group applies.  
- **divisible** A "1" if the bid is divisible or empty if it is indivisible. A "2" if the bid is "mixed" divisible.
- **label**  A string to aid interpreting the results.