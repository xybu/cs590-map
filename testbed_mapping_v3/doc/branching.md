This doc discusses how PM elimination is changed.


How branching works?

PM {A, B, C, D} =>
  PM {A, C, D} =>
     PM {A, D}
  PM {B, C, D} =>

Early stop of branching?

If some result is dominated by a previous result, we stop the branch.

Stop immediately or allow for a few more rounds -- consecutive dominance?
