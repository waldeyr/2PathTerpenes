# MOLECULES DEFNITIONS
# Helper para compatibilidade com versões antigas (0.8.0) e novas (1.0+) de MØD
try:
    from mod import Graph
except ImportError:
    pass

# Garantir que Graph exista e possua os métodos adequados
if 'Graph' not in globals():
    class GraphCompat:
        @staticmethod
        def fromDFS(*args, **kwargs):
            return graphDFS(*args, **kwargs)
        @staticmethod
        def fromSMILES(*args, **kwargs):
            return smiles(*args, **kwargs)
    Graph = GraphCompat
else:
    if not hasattr(Graph, 'fromDFS') and 'graphDFS' in globals():
        Graph.fromDFS = staticmethod(graphDFS)
    if not hasattr(Graph, 'fromSMILES') and 'smiles' in globals():
        Graph.fromSMILES = staticmethod(smiles)

######################################
#  PIVOT MOLECULES
######################################
gpp = Graph.fromDFS("CC(=CCCC(=CCOP(=O)(O)OP(=O)(O)O)C)C", "GPP")
fpp = Graph.fromDFS("CC(=CCCC(=CCCC(=CCO[P](=O)(O)O[P](=O)(O)O)C)C)C", "FPP")
npp = Graph.fromDFS("CC(C)=CCCC(C)=CCCC(C)(OP(O)(OP(O)(O)=O)=O)C=C", "NPP")
H = Graph.fromDFS("[H+]", "H+")
H2O = Graph.fromSMILES("[OH2]", "H2O")
######################################
# ANIONS
######################################
opp = Graph.fromDFS("OP(O)(OP(O)([O-])=O)=O", "OPP-")
######################################
# CATIONS
######################################
gCationC1 = Graph.fromSMILES("C([CH2+])=C(C)CCC=C(C)C", "geranyl cation C1+")
gCationC3 = Graph.fromSMILES("C(CC[C+](C=C)C)=C(C)C","geranyl cation C3+")
lpp = Graph.fromSMILES("C(C(C)(CCC=C(C)C)OP(OP(O)(O)=O)(O)=O)=C", "linalyl diphosphate")
alphaTerpinylCation = Graph.fromSMILES("C1CC(CCC=1C)[C+](C)C", "alfa terpinyl cation")
phellandrylCation = Graph.fromSMILES("C1(C)CCC(C(C)C)[CH+]C=1","Phellandryl Cation")
pinylCation = Graph.fromSMILES("C[C+]1CCC2CC1C2(C)C", "Pinyl Cation")
bornylCation = Graph.fromSMILES("CC12CCC(C[CH+]1)C2(C)C", "Bornyl Cation")
penchylCation = Graph.fromSMILES("CC12CC(CC1)C(C)(C)[CH+]2","Penchyl Cation")
isocamphylCation = Graph.fromSMILES("C[C+]1C2CCC(C2)C1(C)C", "Isocamphyl Cation")
phellandrylCationAlternative = Graph.fromSMILES("C1C(CC[C+](C=1)C)C(C)C","Phellandryl Cation Alternative")
terpinen4YlCation = Graph.fromSMILES("C1C[C+](CCC=1C)C(C)C", "Terpinen-4-yl-cation")
thujylCation = Graph.fromSMILES("C[C+]1CCC2(CC21)C(C)C","Thujyl Cation")
######################################
# TARGET MOLECULES
######################################
alphaTerpinol = Graph.fromSMILES("CC1=CCC(CC1)C(C)(C)O", "alpha-terpinol")
limonene = Graph.fromSMILES("CC1=CCC(CC1)C(=C)C","limonene")
terpinolene = Graph.fromSMILES("C1CC(CCC=1C)=C(C)C","terpinolene")
betaPinene = Graph.fromSMILES("CC1(C2CCC(=C)C1C2)C","beta Pinene")
alfaPinene = Graph.fromSMILES("C1CC2CC(C=1C)C2(C)C","alfa Pinene")
car3Ene = Graph.fromSMILES("C1CC2C(C)(C)[CH2]2CC=1C","car-3-ene")
fenchol = Graph.fromSMILES("CC1(C)C(C2(C)CCC1C2)O","fenchol")
camphene = Graph.fromSMILES("CC1(C2CCC(C2)C1=C)C","camphene")
bornylDisphophate = Graph.fromSMILES("CC1(C)C2CC(C1(C)CC2)OP(OP(O)(O)=O)(O)=O", "bornyl diphosphate")
betaPhellandrene = Graph.fromSMILES("C1C(CCC(C=1)=C)C(C)C", "beta phellandrene")
gammaTerpinene = Graph.fromSMILES("C1(C(C)C)CC=C(C)CC=1","gamma terpinene")
sabinene = Graph.fromSMILES("C=C1CCC2(CC12)C(C)C","sabinene")
mycerne = Graph.fromSMILES("C=C(C=C)CCC=C(C)C","myrcene")
betaOcimene = Graph.fromSMILES("CC(=CCC=C(C)C=C)C","beta-ocimene")
linalool = Graph.fromSMILES("C(C(C)(CCC=C(C)C)O)=C","linalool")
geraniol = Graph.fromSMILES("C(CO)=C(C)CCC=C(C)C","geraniol")
cineole18 = Graph.fromSMILES("[CH]1CC2CCC1(C)OC2(C)C", "1,8-cineole")
