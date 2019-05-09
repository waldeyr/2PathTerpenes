######################################
#  DRAW RULES
######################################
# GRAMMAR
ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
######################################
# RULES
######################################
pushFilePrefix("rules/")
r15 = ruleGML('5-7-closure.gml')
r16 = ruleGML("1-8-cyc.gml")
popFilePrefix()

p = DGPrinter()
p.graphPrinter.collapseHydrogens = False

postSection("Rules")
for r in inputRules:
	r.print()
