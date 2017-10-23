# Content Review Tool
Content review tool (CRT) software useful for anyone wanting to review content in bulk or apply labels to large datasets. This implementation used data from the Reddit API as fodder for review, but this tool is extensible to other usecases with a few edits to seed.py.

### TL;DR ###
* This was built as a final project for the Hackbright software engineering fellowship in October 2017
* Over 2000 lines of coding, about 75% back-end. 
* Code includes a classifier for Reddit comment safety, implemented with scikit-learn 
* Adding an additional rule heuristic on top of the ML classifier allows us to automate comment safety verdicts in about 25% of cases with a less than 1% error rate. 


### Getting Started ###
The training page shows new reviewers how to get started and highlights some queue features including blurring, hotkeys, and batch submissions. 

<kbd><img align="center" src="/static/images/training.png" /></kbd>


### The Queue ###
Within the queue, reviewers see the comment or image for review as well as additional contextualizing information about the review item. If a comment contains a badword, the reviewer will see a banner indicating the content is potentially unsafe. In the image below you can also see the nav bar, with increments daily reviews with each batch submission so the reviewer can see progress. Review verdicts are only added to the db  

<kbd><img align="center" src="/static/images/queue.png" /></kbd>

### Dashboards ###
The tool has both operational and insights dashboards. A few tables highlighted below. 

<kbd><img align="center" height:"500" src="/static/images/agreementrate.png" /></kbd>

<kbd><img align="center" height:"500" src="/static/images/classifier.png" /></kbd>

<kbd><img align="center" height:"500" src="/static/images/insights.png" /></kbd>

### Questions? ###
Made by [@aliglenesk])(https://twitter.com/aliglenesk)