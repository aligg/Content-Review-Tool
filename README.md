# Content Review Tool
Content review tool (CRT) software useful for anyone wanting to review content in bulk or apply labels to large datasets. This implementation uses data from the Reddit API as fodder for review, but this tool is extensible to other use cases with a few edits to seed.py.

### TL;DR ###
* Built as a final project for the Hackbright software engineering fellowship in October 2017
* Over 2500 lines of code, about 75% back-end. 
* Includes a classifier for Reddit comment safety, implemented with scikit-learn 
* Adding an additional rule heuristic on top of the ML classifier allows us to automate comment safety verdicts in about 25% of cases with a less than 1% error rate. 

### Getting Started ###
The training page shows new reviewers how to get started and highlights some queue features including blurring, hotkeys, and batch submissions. 

<kbd><img align="center" src="/static/images/training.png" width="600" align="center" /></kbd>

### The Queue ###
Within the queue, reviewers see the comment or image for review as well as additional contextualizing information about the review item. If a comment contains a badword, the reviewer will see a banner indicating the content is potentially unsafe. In the image below you can also see the nav bar, with increments daily reviews with each batch submission so the reviewer can see progress. Review verdicts are only added to the db  

<kbd><img align="center" src="/static/images/queue.png" width="600" align="center" /></kbd>

### Dashboards ###
The tool has both operational and insights dashboards. The queue includes back-end logic that a reviewer can only review an item once, and an item can be reviewed by different reviewers up to 3 times. Average agreement rate between reviewers across items shown in the agreement rate chart below. The classifier doesn't reach a level of precision that would allow for automation, so within the tool there are additional rules added, considering attributes like account age, karma, or whether or not the subreddit is NSFW. Combing the ML classifier with the heuristic allows us to automate verdicts with a very low error rate - shown in the second chart below. The last table below a safety score by subreddit. The safety score is calculated using solely what percentage of comments on that subreddit are rated as safe. 

<kbd><img src="/static/images/agreementrate.png" width="600" align="center" /></kbd>

<kbd><img src="/static/images/classifier.png"  width="600" align="center" /></kbd>

<kbd><img src="/static/images/insights.png"  width="600" align="center" /></kbd>

### Questions? ###
Made by [@aliglenesk](https://twitter.com/aliglenesk)