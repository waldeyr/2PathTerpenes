import os

import progress_utils

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

r00 = Rule.fromGMLFile('sesqui_deltaCadinene_OxyReduction.gml')
r01 = Rule.fromGMLFile('sesqui_Cope01.gml')
r02 = Rule.fromGMLFile('sesqui_Cope02.gml')
r03 = Rule.fromGMLFile('sesqui_C7_protonation.gml')
r04 = Rule.fromGMLFile('sesqui_C2_protonation.gml')
r05 = Rule.fromGMLFile('sesqui_BicycloGermacrenes_C3_Oxidation.gml')
r06 = Rule.fromGMLFile('sesqui_7_11_Cyc.gml')
r07 = Rule.fromGMLFile('sesqui_6_2_Cyc_For_Germacrenoids.gml')
r08 = Rule.fromGMLFile('sesqui_6_1_Cyc.gml')
r09 = Rule.fromGMLFile('sesqui_2_10_Cyc.gml')
r10 = Rule.fromGMLFile('sesqui_2_7_Cyc.gml')
r11 = Rule.fromGMLFile('sesqui_2_6_Cyc.gml')
r12 = Rule.fromGMLFile('sesqui_1_11_Cyc.gml')
r13 = Rule.fromGMLFile('sesqui_1_10_Cyc.gml')
r14 = Rule.fromGMLFile('mono_penchyl_cation_fechon.gml')
r15 = Rule.fromGMLFile('mono_opp_loss_for_lpp_c3_alternative.gml')
r16 = Rule.fromGMLFile('mono_opp_loss_for_lpp_c3.gml')
r17 = Rule.fromGMLFile('mono_opp_gain_by_bornyl_cation.gml')
r18 = Rule.fromGMLFile('mono_bornyl_cation_bornyl_diphosphate.gml')
r19 = Rule.fromGMLFile('common_Wagner_Meervein.gml')
r20 = Rule.fromGMLFile('mono_3_7_Cyc.gml')
r21 = Rule.fromGMLFile('mono_2_7_Cyc.gml')
r22 = Rule.fromGMLFile('mono_2_6_Cyc.gml')
r23 = Rule.fromGMLFile('mono_1_8_Cyc.gml')
r24 = Rule.fromGMLFile('common_opp_loss_alternative.gml')
r25 = Rule.fromGMLFile('common_opp_loss.gml')
r26 = Rule.fromGMLFile('common_opp_gain_by_cation_alternative.gml')
r27 = Rule.fromGMLFile('common_opp_gain_by_cation.gml')
r28 = Rule.fromGMLFile('common_h_loss.gml')
r29 = Rule.fromGMLFile('common_h2o_gain.gml')
r30 = Rule.fromGMLFile('common_allyls_shift.gml')
r31 = Rule.fromGMLFile('common_1-3_H_shift.gml')
r32 = Rule.fromGMLFile('common_1-2_H_shift.gml')
r33 = Rule.fromGMLFile('common_1_6_Cyc.gml')

popFilePrefix()
######################################
# DEFINE LIST OF INITIAL INPUTS
######################################
eductMols = [gpp,fpp,H2O]

######################################
# ITERATIONS
######################################

iterations = int(os.environ.get("SIMULATION_ITERATIONS", "7"))
if iterations < 1:
    raise ValueError("SIMULATION_ITERATIONS must be at least 1")
strat = (addSubset(eductMols) >> repeat[iterations](inputRules))

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
with progress_utils.phase("Phase 2/4: Building derivation graph (MOD DPO)"):
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
