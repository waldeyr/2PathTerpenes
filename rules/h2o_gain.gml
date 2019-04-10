# Processes Special Issue "In Silico Metabolic Modeling and Engineering"
rule [
    ruleID "Capture of H2O"
    left [
        node [ id 1 label "C+" ]
        node [ id 2 label "H" ]
        edge [ source 2 target 3 label "-" ]
    ]
    context [
        node [ id 3 label "O" ]
        node [ id 4 label "H" ]	
        edge [ source 3 target 4 label "-" ]
    ]
    right [
        node [ id 1 label "C" ]
        node [ id 2 label "H+" ]
        edge [ source 1 target 3 label "-" ]
    ]
]
