# Market Design

This project is a python implementation of the market mechanism described in the paper
["Shapley value based pricing for auctions and exchanges" (Lindsay 2018)](https://doi.org/10.1016/j.geb.2017.10.020).  The project uses a [bidding language](docs/bidding_language.md) that extends the version in the
paper to allow bidders to express their preferences more concisely.


# Installing on Windows
Install [git](https://git-scm.com/downloads) and [Python 3.x](https://www.python.org/downloads/) if not already installed.


```
# Get a copy of the project. 
git clone https://github.com/luke777/marketdesign.git
# Set up and activate the virtual environment 
cd marketdesign
py -m venv env
env\Scripts\activate
py -m pip install -r requirements.txt
# Verify that the command-line solver runs
py solver.py examples\Lindsay2018_t1_seller_and_2_buyers.txt

```

Note, these instructions are for Windows.  On Linux/macOS try using `python3` instead of `py` to run python 
and `source env/bin/activate` instead of `.\env\Scripts\activate` to activate the virtual environment.

# Command-line solver
The program `solver.py` reads in bids from a file and outputs the 
winning bids and payments.  If the python virtual environment is not already activated, activate is as follows. \
`env\Scripts\activate` \
The solver can then be run.  
`py solver.py examples\Lindsay2018_t1_seller_and_2_buyers.txt`

Three file formats are supported.
The directory `examples` contains examples of each of the formats.  The cases are taken from Lindsay 2018.

- **[Text](docs/txt_bids.md)**  This format is the most concise.  Bids are specified in a text file
with one line per bidder.

- **[CSV](docs/csv_bids.md)** This format is convenient if bids are prepared in a spreadsheet.

- **[JSON](https://luke777.github.io/marketdesign/web/static/apidoc/index.html)**  This format is relatively more verbose but allows bids 
to be easily prepared and analyzed using most programming languages.

By default, the results of solving the market are shown onscreen.  The output can 
be directed to a file as follows. \
`py solver.py examples\Lindsay2018_t2.1_two_demand_types.csv -o output.json` \
The format of the output is determined by the filename extension.  As with inputs, 
the supported formats are text (.txt), csv, and json.

# Web solver
The program `web-solver.py` starts a micro web service that allows the 
market solver to be accessed online.

If the python virtual environment is not already activated, activate it with
`env\Scripts\activate` \
Then start the service with \
`py web-solver.py` 

Opening `http://localhost:5000` in a browser should display links to the following. 
- A form for submitting bids in text format.
- A form for uploading a file with bids in cvs format.
- A form for submitting bids in json format.
- An example of a graphical interface that lets users experiment 
with different bids.  The bids are captured using javascript
and sent to the server in json format.

