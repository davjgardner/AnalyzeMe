# AnalyzeMe

Utility to analyze GroupMe conversations. Features include plotting message frequency over time, identifying message hotspots through the day, and printing the downloaded conversation data in a human-readable format.

## Setup

1. Download conversations:

   On the GroupMe website, click the "My Profile" icon, then "Export My Data".
   This will give the option to download the data from any group or direct message chain.

2. Extract the resulting zip file, and then point `AnalyzeMe.py` at the `message.json`
   for the relevant chat.
3. Make sure the required python modules, `numpy` and `matplotlib`, are installed.

## Usage

Call `AnalyzeMe.py` as follows:

`$ ./AnalyzeMe.py command path/to/message.json`

For example,

* `$ ./AnalyzeMe.py len message.json --plot`

* `$ ./AnalyzeMe.py readable message.json -o output.txt`

For help on a specific command, run `./AnalyzeMe.py command --help`

Use `./AnalyzeMe.py --help` for a list of supported commands.
