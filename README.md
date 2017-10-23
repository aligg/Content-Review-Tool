# Content Review Tool
Content review tool (CRT) software useful for anyone wanting to review content in bulk or apply labels to large datasets. This implementation used data from the Reddit API as fodder for review, but this tool is extensible to other usecases with a few edits to seed.py.

### TL;DR ###
* This was built as a final project for the Hackbright software engineering fellowship in October 2017
* Over 2000 lines of coding, about 75% back-end. 
* Code includes a classifier for Reddit comment safety, implemented with scikit-learn 
* Adding an additional rule heuristic on top of the ML classifier allows us to automate comment safety verdicts in about 25% of cases with a less than 1% error rate. 

### Getting Started ###
The training page shows new reviewers how to get started and highlights some queue features including blurring, hotkeys, and batch submissions. 

![Getting Started](/static/images/training.png)
<kbd><img src="/static/images/training.png" /></kbd>



### The Queue ###
