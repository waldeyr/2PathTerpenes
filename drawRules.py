######################################
#  DRAW RULES
######################################
# GRAMMAR
ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
######################################
# RULES
######################################
pushFilePrefix("rules/")
opp_loss_gpp = ruleGML('opp_loss_gpp.gml')
opp_loss_gpp = ruleGML('opp_loss_gpp_alternative.gml')
h_loss = ruleGML("h_loss.gml")
h2o_gain = ruleGML("h2o_gain.gml")
popFilePrefix()

postSection("Rules")
for r in inputRules:
	r.print()
