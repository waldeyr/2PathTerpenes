# Helper for MØD compatibility
try:
    from mod import Rule, post
except ImportError:
    pass

if 'Rule' not in globals():
    class RuleCompat:
        @staticmethod
        def fromGMLFile(*args, **kwargs):
            return ruleGML(*args, **kwargs)
    Rule = RuleCompat

pushFilePrefix("rules/")

rules_files = [
    "sesqui_deltaCadinene_OxyReduction.gml",
    "sesqui_Cope01.gml",
    "sesqui_Cope02.gml",
    "sesqui_C7_protonation.gml",
    "sesqui_C2_protonation.gml",
    "sesqui_BicycloGermacrenes_C3_Oxidation.gml",
    "sesqui_7_11_Cyc.gml",
    "sesqui_6_2_Cyc_For_Germacrenoids.gml",
    "sesqui_6_1_Cyc.gml",
    "sesqui_2_10_Cyc.gml",
    "sesqui_2_7_Cyc.gml",
    "sesqui_2_6_Cyc.gml",
    "sesqui_1_11_Cyc.gml",
    "sesqui_1_10_Cyc.gml",
    "mono_penchyl_cation_fechon.gml",
    "mono_opp_loss_for_lpp_c3_alternative.gml",
    "mono_opp_loss_for_lpp_c3.gml",
    "mono_opp_gain_by_bornyl_cation.gml",
    "mono_bornyl_cation_bornyl_diphosphate.gml",
    "common_Wagner_Meervein.gml",
    "mono_3_7_Cyc.gml",
    "mono_2_7_Cyc.gml",
    "mono_2_6_Cyc.gml",
    "mono_1_8_Cyc.gml",
    "common_opp_loss_alternative.gml",
    "common_opp_loss.gml",
    "common_opp_gain_by_cation_alternative.gml",
    "common_opp_gain_by_cation.gml",
    "common_h_loss.gml",
    "common_h2o_gain.gml",
    "common_allyls_shift.gml",
    "common_1-3_H_shift.gml",
    "common_1-2_H_shift.gml",
    "common_1_6_Cyc.gml"
]

post.summarySection("Rules Previews")

# Print all 34 rules
for f in rules_files:
    r = Rule.fromGMLFile(f)
    r.print()

popFilePrefix()
