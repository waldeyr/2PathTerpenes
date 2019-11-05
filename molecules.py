# MOLECULES DEFNITIONS
######################################
#  PIVOT MOLECULES
######################################
gpp = graphDFS("CC(=CCCC(=CCOP(=O)(O)OP(=O)(O)O)C)C", "GPP")
fpp = graphDFS("CC(=CCCC(=CCCC(=CCO[P](=O)(O)O[P](=O)(O)O)C)C)C", "FPP")
npp = graphDFS("CC(C)=CCCC(C)=CCCC(C)(OP(O)(OP(O)(O)=O)=O)C=C", "NPP")
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
cineole18 = smiles("[CH]1CC2CCC1(C)OC2(C)C", "1,8-cineole")
