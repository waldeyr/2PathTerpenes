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
r07 = ruleGML('opp_loss_for_lpp_c3.gml')
r08 = ruleGML('opp_loss_for_lpp_c3_alternative.gml')
r09 = ruleGML('1-6-closure.gml')
r10 = ruleGML('3,7-closure.gml')
r11 = ruleGML('2,7-closure.gml')
r12 = ruleGML('WMshift.gml')
r13 = ruleGML('1-8-cyc.gml')
r14 = ruleGML('2-6-closure.gml')
r15 = ruleGML('5-7-closure.gml')
r16 = ruleGML ('opp_gain_by_bornyl_cation.gml')
r17 = ruleGML ('allylshift.gml')
popFilePrefix()
######################################
# DEFINE LIST OF INITIAL INPUTS
######################################
#eductMols = [alphaTerpinol,H2O]
eductMols = [gpp,H2O]
######################################
# HYPERGRAPH GENERATION
######################################
ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
# comput overall charge of molecule
def overallCharge(a):
    return sum(int(v.charge) for v in a.vertices)
# calculate the cyclomatic number
def countCycs(a):
        return a.numEdges - a.numVertices + 1
# a general breadth-first expansion strategy
strat = (addSubset(eductMols) >> repeat[7](inputRules))
# calculate derivation graph (hypergraph)
dg = dgRuleComp(inputGraphs, strat, ls)
dg.calc()
