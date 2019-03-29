######################################
#  DRAW RULES
######################################
# GRAMMAR
ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
######################################
# RULES
######################################
pushFilePrefix("../rules/")
opp_loss_for_fpp = ruleGML('opp_loss_for_fpp.gml')
opp_loss_for_npp_c1 = ruleGML('opp_loss_for_npp_c1.gml')
opp_loss_for_npp_c3 = ruleGML('opp_loss_for_npp_c3.gml')
opp_gain_by_farnesyl_cation = ruleGML('opp_gain_by_farnesyl_cation.gml')
fpp_1_10_cyc = ruleGML("fpp-1-10Cyc.gml")
fpp_1_11_cyc = ruleGML("fpp-1-11Cyc.gml")
ring_closure_c2_c10 = ruleGML("2-10Cyc.gml")
h_shift_c1_c2 = ruleGML("1-2Hshift.gml")
h_shift_c1_c3 = ruleGML("1-3Hshift.gml")
h_loss = ruleGML("h_loss.gml")
h2o_gain = ruleGML("h2o_gain.gml")
popFilePrefix()

postSection("Rules")
for r in inputRules:
	r.print()
