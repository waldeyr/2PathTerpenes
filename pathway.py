## print target molecule
postSection("Target Molecule")
target.print()

## setup integer hyperflow problem
config.ilp.solverVerbose = True
flow = dgFlow(dg)

## add eductMols as potential flow source(s)
for m in eductMols: flow.addSource(m) 

## add flow sink(s)
for a in dg.vertexGraphs: flow.addSink(a)

## set constraints and objective function
flow.addConstraint(outFlow(target) >= 1)
#flow.objectiveFunction = edge  # minimize overall edge flow, which is the default anyway
#flow.objectiveFunction = isEdgeUsed  # minimize number of edges with non-zero flow

## solve the integer hyperflow problem
#flow.setSolverEnumerateBy(maxNumSolutions=10)  # enumerate at most 10 soluions
flow.calc()
flow.solutions.list()

## print flow solution of pathway query
flowPrinter = DGFlowPrinter()
flowPrinter.printUnfiltered = True
flow.solutions.print(flowPrinter)
