

######################################
# RULES
######################################
pushFilePrefix("rules/")


r00 = ruleGML('1-2Hshift.gml')

r01 = ruleGML('1-3Hshift.gml')

r02 = ruleGML('h_loss.gml')

r03 = ruleGML('h2o_gain.gml')

r04 = ruleGML('opp_loss_gpp.gml')

r05 = ruleGML('opp_loss_gpp_alternative.gml')

r06 = ruleGML('opp_gain_by_geranyl_cation.gml')

popFilePrefix()
######################################
# DEFINE LIST OF INITIAL INPUTS
######################################
eductMols = [gpp,H2O]

######################################
# ITERATIONS
######################################


strat = (addSubset(eductMols) >> repeat[3](inputRules))

######################################
# NETWORK GENERATION
######################################
ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
def overallCharge(a): return sum(int(v.charge) for v in a.vertices)
def countCycs(a): return a.numEdges - a.numVertices + 1
dg = dgRuleComp(inputGraphs, strat, ls)
dg.calc()
