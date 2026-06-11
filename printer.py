# Helper para compatibilidade com versões antigas (0.8.0) e novas (1.0+) de MØD
try:
    from mod import DGPrinter
    try:
        from mod import post
        if not hasattr(post, 'summarySection'):
            raise ImportError
    except ImportError:
        try:
            from mod import postSection as legacyPostSection
            class PostCompat:
                @staticmethod
                def summarySection(heading):
                    legacyPostSection(heading)
            post = PostCompat
        except ImportError:
            class PostDummy:
                @staticmethod
                def summarySection(heading):
                    pass
            post = PostDummy
except ImportError:
    pass

######################################
# PDF PRINTER
######################################
p = DGPrinter()
# print molecule with all the hydrogenes attached
p.graphPrinter.collapseHydrogens = True
p.graphPrinter.withIndex = False

# Callback compatível com ambas as assinaturas:
# MØD v0.8.0: lambda g, dg: ...
# MØD v1.0.0+: lambda v: ...
def vertex_colour_cb(*args):
    g = args[0] if len(args) == 2 else args[0].graph
    return "red" if overallCharge(g) != 0 else "black" if countCycs(g) > 0 else "black"

p.pushVertexColour(vertex_colour_cb)

post.summarySection("Plant Monoterpenes Biosynthesis")
dg.print(p)

