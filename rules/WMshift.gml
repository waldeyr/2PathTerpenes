# Processes Special Issue "In Silico Metabolic Modeling and Engineering"
# Rule refrence:  (Christianson, 2017) https://doi.org/10.1021/acs.chemrev.7b00287
rule [
    ruleID "Wagner-Meerwein 1,2 alcyl shift"
    left [
        node [ id 1 label "C+" ]
        node [ id 2 label "C"  ]
        edge [ source 2 target 3 label "-" ]
    ]
    context [
    node [ id 3 label "C" ]
    edge [ source 1 target 2 label "-" ] 
    ]
    right [
        node [ id 1 label "C" ]
        node [ id 2 label "C+" ]
        edge [ source 1 target 3 label "-" ]
    ]
]