######################################
# PDF PRINTER
######################################
p = DGPrinter()
# print molecule with all the hydrogenes attached
p.graphPrinter.collapseHydrogens = True
p.graphPrinter.withIndex = False
# color molecules with rings red, charged molecules blue
p.pushVertexColour(lambda g, dg: "red" if overallCharge(g) != 0 else "black" if countCycs(g) > 0 else "black")

postSection("Plant Monoterpenes Biosynthesis")
dg.print(p)

#postSection("Rules")
#for r in inputRules:
#	r.print()

# Print product SMILES to stdout
#for v in dg.vertices:
#    m = v.graph
#    if m.isMolecule:
#        print(m.name, m.smiles)
#    else:
#        print(m.name, m.graphDFS)    
