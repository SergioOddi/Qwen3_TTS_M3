"""
Preprocessore di testo per terminologia biochimica e scientifica.

Converte sigle, formule chimiche e notazioni tecniche in forma leggibile
per modelli TTS, mantenendo pronuncia corretta in contesto accademico.
"""

import re
from typing import Dict, List, Tuple


class BiochemTextPreprocessor:
    """Preprocessore specializzato per testi di biochimica."""

    def __init__(self):
        # Dizionario formule chimiche comuni
        self.chemical_formulas = {
            # Molecole semplici
            "H2O": "H two O",
            "O2": "O two",
            "CO2": "C O two",
            "N2": "N two",
            "H2": "H two",
            "NH3": "N H three",
            "CH4": "C H four",

            # Acidi
            "HCl": "H C L",
            "H2SO4": "H two S O four",
            "HNO3": "H N O three",

            # Coenzimi e nucleotidi
            "ATP": "A T P",
            "ADP": "A D P",
            "AMP": "A M P",
            "NAD+": "N A D plus",
            "NADH": "N A D H",
            "NADP+": "N A D P plus",
            "NADPH": "N A D P H",
            "FAD": "F A D",
            "FADH2": "F A D H two",
            "CoA": "Coenzyme A",
            "GTP": "G T P",
            "GDP": "G D P",
            "CTP": "C T P",
            "UTP": "U T P",

            # DNA/RNA
            "DNA": "D N A",
            "RNA": "R N A",
            "mRNA": "messenger R N A",
            "tRNA": "transfer R N A",
            "rRNA": "ribosomal R N A",
            "cDNA": "complementary D N A",

            # Aminoacidi (abbreviazioni 3 lettere)
            "Ala": "Alanine",
            "Arg": "Arginine",
            "Asn": "Asparagine",
            "Asp": "Aspartate",
            "Cys": "Cysteine",
            "Gln": "Glutamine",
            "Glu": "Glutamate",
            "Gly": "Glycine",
            "His": "Histidine",
            "Ile": "Isoleucine",
            "Leu": "Leucine",
            "Lys": "Lysine",
            "Met": "Methionine",
            "Phe": "Phenylalanine",
            "Pro": "Proline",
            "Ser": "Serine",
            "Thr": "Threonine",
            "Trp": "Tryptophan",
            "Tyr": "Tyrosine",
            "Val": "Valine",
        }

        # Ioni comuni
        self.ions = {
            "Na+": "sodium ion",
            "K+": "potassium ion",
            "Ca2+": "calcium ion",
            "Mg2+": "magnesium ion",
            "Fe2+": "ferrous ion",
            "Fe3+": "ferric ion",
            "Cl-": "chloride ion",
            "OH-": "hydroxide ion",
            "H+": "proton",
            "Zn2+": "zinc ion",
            "Cu2+": "copper ion",
            "Mn2+": "manganese ion",
        }

        # Acronimi biochimici comuni
        self.acronyms = {
            "pH": "P H",
            "pKa": "P K A",
            "Km": "K M",
            "Vmax": "V max",
            "kcat": "K cat",
            "PKA": "protein kinase A",
            "PKC": "protein kinase C",
            "PCR": "P C R",
            "ELISA": "E L I S A",
            "SDS-PAGE": "S D S PAGE",
            "HPLC": "H P L C",
            "NMR": "N M R",
            "UV": "U V",
            "IR": "I R",
        }

        # Pattern per numeri con subscript/superscript
        self.subscript_pattern = re.compile(r'([A-Z][a-z]?)(\d+)')
        self.superscript_pattern = re.compile(r'([A-Z][a-z]?)(\d+)\+')

    def preprocess(self, text: str) -> str:
        """
        Preprocessa testo biochimico per TTS.

        Args:
            text: Testo originale con terminologia scientifica

        Returns:
            Testo processato con pronuncia corretta
        """
        # 1. Sostituisci ioni (prima, perché contengono caratteri speciali)
        for ion, pronunciation in self.ions.items():
            # Usa word boundary per evitare sostituzioni parziali
            text = re.sub(r'\b' + re.escape(ion) + r'\b', pronunciation, text)

        # 2. Sostituisci formule chimiche comuni
        for formula, pronunciation in self.chemical_formulas.items():
            text = re.sub(r'\b' + re.escape(formula) + r'\b', pronunciation, text)

        # 3. Sostituisci acronimi
        for acronym, pronunciation in self.acronyms.items():
            text = re.sub(r'\b' + re.escape(acronym) + r'\b', pronunciation, text)

        # 4. Gestisci pattern generici (es. H3PO4 -> H three P O four)
        text = self._process_generic_formulas(text)

        # 5. Gestisci unità di misura
        text = self._process_units(text)

        # 6. Gestisci numeri con esponenti (es. 10^-7 -> 10 to the power of negative 7)
        text = self._process_exponents(text)

        return text

    def _process_generic_formulas(self, text: str) -> str:
        """Processa formule chimiche generiche non nel dizionario."""
        # Pattern: Lettera maiuscola opzionalmente seguita da minuscola, poi numero
        # Es: H2, Ca2, O3
        def replace_subscript(match):
            element = match.group(1)
            number = match.group(2)
            # Se non è già stata sostituita
            return f"{element} {number}"

        # Solo se non contiene spazi (per evitare di processare testo già processato)
        words = text.split()
        processed_words = []

        for word in words:
            # Controlla se è una formula chimica (contiene lettere maiuscole e numeri)
            if re.search(r'[A-Z][a-z]?\d', word) and not ' ' in word:
                # Processa subscript
                word = self.subscript_pattern.sub(replace_subscript, word)
            processed_words.append(word)

        return ' '.join(processed_words)

    def _process_units(self, text: str) -> str:
        """Processa unità di misura scientifiche."""
        units = {
            "mM": "millimolar",
            "μM": "micromolar",
            "nM": "nanomolar",
            "M": " molar",  # Spazio per evitare conflitti con M in altre parole
            "mg/mL": "milligrams per milliliter",
            "μg/mL": "micrograms per milliliter",
            "ng/mL": "nanograms per milliliter",
            "kDa": "kilodaltons",
            "Da": "daltons",
            "bp": "base pairs",
            "kb": "kilobase pairs",
            "ºC": "degrees Celsius",
            "°C": "degrees Celsius",
            "nm": "nanometers",
            "μm": "micrometers",
            "mL": "milliliters",
            "μL": "microliters",
        }

        for unit, pronunciation in units.items():
            text = re.sub(r'\b' + re.escape(unit) + r'\b', pronunciation, text)

        return text

    def _process_exponents(self, text: str) -> str:
        """Processa notazione esponenziale."""
        # Pattern: 10^-7, 10^7, e^-x, etc.
        def replace_exponent(match):
            base = match.group(1)
            sign = match.group(2) if match.group(2) else ""
            exp = match.group(3)

            sign_word = "negative " if sign == "-" else ""
            return f"{base} to the power of {sign_word}{exp}"

        # Match: numero^(opzionale segno)numero
        text = re.sub(r'(\d+|\w)\^(-?)(\d+)', replace_exponent, text)

        return text

    def add_custom_mappings(self, mappings: Dict[str, str], category: str = "custom"):
        """
        Aggiungi mappings personalizzati.

        Args:
            mappings: Dizionario termine -> pronuncia
            category: Categoria (chemical_formulas, ions, acronyms)
        """
        if category == "chemical_formulas":
            self.chemical_formulas.update(mappings)
        elif category == "ions":
            self.ions.update(mappings)
        elif category == "acronyms":
            self.acronyms.update(mappings)
        else:
            # Crea nuova categoria personalizzata
            if not hasattr(self, 'custom_mappings'):
                self.custom_mappings = {}
            self.custom_mappings.update(mappings)


def preprocess_biochem_text(text: str, custom_mappings: Dict[str, str] = None) -> str:
    """
    Funzione helper per preprocessare velocemente testo biochimico.

    Args:
        text: Testo originale
        custom_mappings: Mappings personalizzati opzionali

    Returns:
        Testo processato
    """
    preprocessor = BiochemTextPreprocessor()

    if custom_mappings:
        preprocessor.add_custom_mappings(custom_mappings)

    return preprocessor.preprocess(text)


# Esempi di utilizzo
if __name__ == "__main__":
    # Test del preprocessore
    test_texts = [
        "The reaction requires ATP and Mg2+ ions at pH 7.4.",
        "Ca2+ activates the enzyme, while H2O acts as a substrate.",
        "The concentration of NADH was 5 mM in the solution.",
        "DNA polymerase synthesizes RNA from nucleotides like ATP, GTP, CTP, and UTP.",
        "The Km value for this enzyme is 10^-7 M.",
        "Fe2+ can be oxidized to Fe3+ in the presence of O2.",
        "The protein contains Cys, Met, and His residues.",
    ]

    preprocessor = BiochemTextPreprocessor()

    print("=== Biochemical Text Preprocessor Test ===\n")
    for i, text in enumerate(test_texts, 1):
        processed = preprocessor.preprocess(text)
        print(f"Test {i}:")
        print(f"Original:  {text}")
        print(f"Processed: {processed}")
        print()
