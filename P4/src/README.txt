P4 Heuristics

-- Recipe Methods --
We ordered the 'have_enough' checks in our recipe methods using a reference list
Checks were ordered by tools and then items in reducing complexity
We found this was most agreeable for the program as it only made what was necessary at each stage
Smaller items could be added to more complex recipes nearer to the end

-- Recipe Method Declaration --
Recipes were ordered so that the faster methods of production were called first

-- Runtime Heuristics --
We pruned any branches which attempted to produce a tool already obtained
We pruned any branches which attempted to produce more items than were called for
We pruned any branches which attempted to use a tool which would ultimately be inefficient