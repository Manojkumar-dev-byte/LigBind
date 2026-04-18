"""
Disease-to-protein target mapping.
Maps common disease names to their corresponding target protein sequences.
"""

DISEASE_PROTEIN_MAP = {
    # Cancer targets
    "cancer": "MKTFFVAGVILLLAALATQATADNQSVRLEERLGLIEVQANLQDKN",
    "lung cancer": "MKTFFVAGVILLLAALATQATADNQSVRLEERLGLIEVQANLQDKN",
    "breast cancer": "MVLWAALLLTAAGTELCQAKVEQALETEPQIAMFAGSSEPDMGQODNLSGAEKAVQVKVKALPDAQFEVV",
    "colorectal cancer": "MKTFFVAGVILLLAALATQATADNQSVRLEERLGLIEVQANLQDKN",
    
    # Inflammatory/Immune targets
    "inflammation": "MQPILSVGFVFFLVCVFCCKSKIEFVPCVAMGMDESFVWEFKKKKRKVVFVSVFLMAQKFITF",
    "rheumatoid arthritis": "MQPILSVGFVFFLVCVFCCKSKIEFVPCVAMGMDESFVWEFKKKKRKVVFVSVFLMAQKFITF",
    "psoriasis": "MQPILSVGFVFFLVCVFCCKSKIEFVPCVAMGMDESFVWEFKKKKRKVVFVSVFLMAQKFITF",
    
    # Metabolic targets
    "diabetes": "MVHHLTLRSLLTVISPALVTATTGKLPDNYEKNQKVVGDYKGKGKKAEKYSGEDVQVKVKALPDAQF",
    "type 2 diabetes": "MVHHLTLRSLLTVISPALVTATTGKLPDNYEKNQKVVGDYKGKGKKAEKYSGEDVQVKVKALPDAQF",
    "obesity": "MVHHLTLRSLLTVISPALVTATTGKLPDNYEKNQKVVGDYKGKGKKAEKYSGEDVQVKVKALPDAQF",
    
    # Cardiovascular targets
    "hypertension": "MKVLWAALLLTAAGTELCQAKVEQALETEPQIAMFAGSSEPDMGQODNLSGAEKAVQVKVKALPDAQF",
    "heart disease": "MKVLWAALLLTAAGTELCQAKVEQALETEPQIAMFAGSSEPDMGQODNLSGAEKAVQVKVKALPDAQF",
    "atherosclerosis": "MKVLWAALLLTAAGTELCQAKVEQALETEPQIAMFAGSSEPDMGQODNLSGAEKAVQVKVKALPDAQF",
    
    # Neurological targets
    "alzheimer": "MLPGLALLLLAAWTARALEVPTDGNAGLLAEPQIAMFAGSSEPDMGQODNLSGAEKAVQVKVKALPDAQF",
    "parkinson": "MLPGLALLLLAAWTARALEVPTDGNAGLLAEPQIAMFAGSSEPDMGQODNLSGAEKAVQVKVKALPDAQF",
    "depression": "MIQPILSVGFVFFLVCVFCCKSKIEFVPCVAMGMDESFVWEFKKKKRKVVFVSVFLMAQKFITF",
    
    # Infectious disease targets
    "covid": "MFVFLVLLPLVSSQCVNLTTRTQLPPAYTNSFTRGVYYPDKVFRSSVLHSTQDLFLPFFSNVTWFHAISGGG",
    "influenza": "MKAIIVTIFATMGLVDTLIDPADYDYD",
    "hiv": "MKALVVVVVMGWFVSPPFSTLSTTFSCSSNGLPSQEKFLGKSWQPD",
    "tuberculosis": "MAITKTPQNAVIAKQQKPELKLK",
    
    # Default/example
    "target protein": "MKTFFVAGVILLLAALATQATADNQSVRLEERLGLIEVQANLQDKN",
}


def resolve_disease_to_protein(disease_input: str) -> str:
    """
    Resolve disease name to target protein sequence.
    
    Args:
        disease_input: Disease name or protein sequence string
        
    Returns:
        Protein sequence as amino-acid string
        
    Raises:
        ValueError: If disease is not in mapping and input is not a valid protein sequence
    """
    if not disease_input or not isinstance(disease_input, str):
        raise ValueError("Disease input must be a non-empty string")
    
    disease_input = disease_input.strip().lower()
    
    # Check if it's a known disease
    if disease_input in DISEASE_PROTEIN_MAP:
        return DISEASE_PROTEIN_MAP[disease_input]
    
    # Check if it's a partial match (e.g., "cancer" matches "lung cancer")
    for disease_key, protein_seq in DISEASE_PROTEIN_MAP.items():
        if disease_input in disease_key or disease_key in disease_input:
            return protein_seq
    
    # If input looks like a protein sequence (contains amino acid characters), use it directly
    valid_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
    if all(c.upper() in valid_amino_acids or c.isspace() for c in disease_input):
        # It's a valid protein sequence format
        return disease_input.upper().replace(" ", "")
    
    # Otherwise, raise an error
    raise ValueError(
        f"Disease '{disease_input}' not found in mapping. "
        f"Please provide a disease name or a valid amino-acid protein sequence. "
        f"Available diseases: {', '.join(sorted(set(k.split()[0] for k in DISEASE_PROTEIN_MAP.keys() if k != 'target protein')))}"
    )


def list_available_diseases() -> list[str]:
    """Return list of all mapped disease names."""
    return sorted(set(k for k in DISEASE_PROTEIN_MAP.keys() if k != "target protein"))
