# Helper para compatibilidade com versões antigas (0.8.0) e novas (1.0+) de MØD
try:
    from mod import Rule, LabelSettings, LabelType, LabelRelation, DG
except ImportError:
    pass

# Garantir que Rule exista e possua os métodos adequados
if 'Rule' not in globals():
    class RuleCompat:
        @staticmethod
        def fromGMLFile(*args, **kwargs):
            return ruleGML(*args, **kwargs)
    Rule = RuleCompat
else:
    if not hasattr(Rule, 'fromGMLFile') and 'ruleGML' in globals():
        Rule.fromGMLFile = staticmethod(ruleGML)

######################################
# RULES
######################################
pushFilePrefix("rules/")

r32 = Rule.fromGMLFile('common_1-2_H_shift.gml')
r28 = Rule.fromGMLFile('common_h_loss.gml')
r29 = Rule.fromGMLFile('common_h2o_gain.gml')
r27 = Rule.fromGMLFile('common_opp_gain_by_cation.gml')
r25 = Rule.fromGMLFile('common_opp_loss.gml')
r24 = Rule.fromGMLFile('common_opp_loss_alternative.gml')

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
# Compatibilidade com a restrição de LabelRelation.Unification do MØD v1.0
try:
    ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
except Exception:
    ls = LabelSettings(LabelType.Term, LabelRelation.Identity)

def overallCharge(a): return sum(int(v.charge) for v in a.vertices)
def countCycs(a): return a.numEdges - a.numVertices + 1

# Instancia o Derivation Graph com o novo build interface do MØD
try:
    # Novo build interface do MØD (v1.0.0+)
    dg = DG(graphDatabase=inputGraphs, labelSettings=ls)
    dg.build().execute(strat)
except (TypeError, AttributeError, Exception):
    # Compatibilidade com versões antigas do MØD (e.g. 0.8.0)
    if 'dgRuleComp' in globals():
        dg = dgRuleComp(inputGraphs, strat, ls)
    elif 'DG' in globals():
        dg = DG(inputGraphs, strat, ls)
    else:
        try:
            dg = DG(inputGraphs, strat, ls)
        except Exception:
            dg = dgRuleComp(inputGraphs, strat, ls)
    dg.calc()
