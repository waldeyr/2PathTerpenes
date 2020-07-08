######################################
# RULES
######################################
pushFilePrefix("rules/")


r32 = ruleGML ('common_1-2_H_shift.gml')

r28 = ruleGML ('common_h_loss.gml')

r29 = ruleGML ('common_h2o_gain.gml')

r27 = ruleGML ('common_opp_gain_by_cation.gml')

r25 = ruleGML ('common_opp_loss.gml')

r24 = ruleGML ('common_opp_loss_alternative.gml')


popFilePrefix()
######################################
# DEFINE LIST OF INITIAL INPUTS
######################################
eductMols = [gpp,fpp,H2O]

######################################
# ITERATIONS
######################################

strat = (addSubset(eductMols) >> repeat[4](inputRules))

######################################
# NETWORK GENERATION
######################################
ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
def overallCharge(a): return sum(int(v.charge) for v in a.vertices)
def countCycs(a): return a.numEdges - a.numVertices + 1
dg = dgRuleComp(inputGraphs, strat, ls)
dg.calc()
