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
# Um DG requer configurações de rótulo que formem uma categoria. Em particular,
# LabelRelation.Unification é inválido aqui no MØD 1.0+; Specialisation mantém
# a semântica de correspondência por termos adequada à geração da rede.
ls = LabelSettings(LabelType.Term, LabelRelation.Specialisation)

def overallCharge(a): return sum(int(v.charge) for v in a.vertices)
def countCycs(a): return a.numEdges - a.numVertices + 1

# Instancia o Derivation Graph com a interface de build do MØD 1.0+.
# A seleção é feita pela API disponível, não por uma captura ampla de exceções:
# falhas de configuração ou de dados devem continuar visíveis para o usuário.
if hasattr(DG, 'build'):
    dg = DG(graphDatabase=inputGraphs, labelSettings=ls)
    dg.build().execute(strat)
else:
    # Compatibilidade com versões antigas do MØD (por exemplo, 0.8.0).
    if 'dgRuleComp' in globals():
        dg = dgRuleComp(inputGraphs, strat, ls)
    else:
        dg = DG(inputGraphs, strat, ls)
    dg.calc()
