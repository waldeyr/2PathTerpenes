######################################
#  PROCESSES SIMULATION 01
#  CONVERSION FPP-NPP
######################################

# GRAMMAR
ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
######################################
#  PIVOT MOLECULES
######################################
gpp = graphDFS("CC(=CCCC(=CCOP(=O)(O)OP(=O)(O)O)C)C", "GPP")
H = graphDFS("[H+]", "H+")
H2O = smiles("[OH2]", "H2O")
######################################
# ANIONS
######################################
opp = graphDFS("OP(O)(OP(O)([O-])=O)=O", "OPP-")
######################################
# CATIONS
######################################
gCationC1 = smiles("C([CH2+])=C(C)CCC=C(C)C", "geranyl cation C1+")
gCationC3 = smiles("C(CC[C+](C=C)C)=C(C)C","geranyl cation C3+")
lpp = smiles("C(C(C)(CCC=C(C)C)OP(OP(O)(O)=O)(O)=O)=C", "linalyl diphosphate")
alphaTerpinylCation = smiles ("C1CC(CCC=1C)[C+](C)C", "alfa terpinyl cation")
#alfaTerpinol = smiles ("C(CO)=C(C)CCC=C(C)C", "alfa terpinol")
phellandrylCation = smiles ("C1(C)CCC(C(C)C)[CH+]C=1","Phellandryl Cation")
pinylCation = smiles ("C[C+]1CCC2CC1C2(C)C", "Pinyl Cation")
bornylCation = smiles ("CC12CCC(C[CH+]1)C2(C)C", "Bornyl Cation")
penchylCation = smiles ("CC12CC(CC1)C(C)(C)[CH+]2","Penchyl Cation")
isocamphylCation = smiles ("C[C+]1C2CCC(C2)C1(C)C", "Isocamphyl Cation")
phellandrylCationAlternative= smiles ("C1C(CC[C+](C=1)C)C(C)C","Phellandryl Cation Alternative")
terpinen4YlCation = smiles ("C1C[C+](CCC=1C)C(C)C", "Terpinen-4-yl-cation")
thujylCation = smiles ("C[C+]1CCC2(CC21)C(C)C","Thujyl Cation")
######################################
# TARGET MOLECULES
######################################
alphaTerpinol = smiles("CC1=CCC(CC1)C(C)(C)O", "alpha-terpinol")
limonene = smiles ("CC1=CCC(CC1)C(=C)C","limonene")
terpinolene = smiles ("C1CC(CCC=1C)=C(C)C","terpinolene")
betaPinene = smiles ("CC1(C2CCC(=C)C1C2)C","beta Pinene")
alfaPinene = smiles ("C1CC2CC(C=1C)C2(C)C","alfa Pinene")
car3Ene = smiles ("C1CC2C(C)(C)[CH2]2CC=1C","car-3-ene")
fenchol = smiles ("CC1(C)C(C2(C)CCC1C2)O","fenchol")
camphene = smiles("CC1(C2CCC(C2)C1=C)C","camphene")
bornylDisphophate = smiles("CC1(C)C2CC(C1(C)CC2)OP(OP(O)(O)=O)(O)=O", "bornyl diphosphate")
betaPhellandrene = smiles("C1C(CCC(C=1)=C)C(C)C", "beta phellandrene")
gammaTerpinene = smiles ("C1(C(C)C)CC=C(C)CC=1","gamma terpinene")
sabinene = smiles ("C=C1CCC2(CC12)C(C)C","sabinene")
mycerne = smiles ("C=C(C=C)CCC=C(C)C","myrcene")
betaOcimene = smiles ("CC(=CCC=C(C)C=C)C","beta-ocimene")
linalool = smiles ("C(C(C)(CCC=C(C)C)O)=C","linalool")
geraniol = smiles ("C(CO)=C(C)CCC=C(C)C","geraniol")
cineole1-8 = smiles("[CH]1CC2CCC1(C)OC2(C)C", "1,8-cineole")
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
#|#####################################

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

######################################
# PDF PRINTER
######################################
p = DGPrinter()
# print molecule with all the hydrogenes attached
p.graphPrinter.collapseHydrogens = True
p.graphPrinter.withIndex = False
# color molecules with rings red, charged molecules blue
p.pushVertexColour(lambda g, dg: "red" if overallCharge(g) != 0 else "black" if countCycs(g) > 0 else "black")

postSection("Generated Hypergraph")
dg.print(p)

postSection("Rules")
for r in inputRules:
	r.print()

# Print product SMILES to stdout
for v in dg.vertices:
    m = v.graph
    if m.isMolecule:
        print(m.name, m.smiles)
    else:
        print(m.name, m.graphDFS)    
