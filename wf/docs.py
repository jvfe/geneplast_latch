from latch.types.metadata import (Fork, ForkBranch, LatchAuthor, LatchMetadata,
                                  LatchParameter, Params, Section, Text, Title)

# TODO: Add some input validation
# TODO: Ask about Title

PARAMS = {
    "sample": LatchParameter(
        display_name="Sample name",
        section_title="Protein Lists",
        description="Dataset from which to estimate evolutionary roots.",
        batch_table_column=True,
    ),
    "species": LatchParameter(
        display_name="Reference species for the rooting analysis",
    ),
    "species_manual": LatchParameter(
        display_name="NCBI taxonomy ID for the reference species to use for rooting"
    ),
    "species_fork": LatchParameter(),
    "cog_mappings_file": LatchParameter(
        display_name="URL to a STRINGdb COG mappings file",
        hidden=True,
    ),
    "clade_names": LatchParameter(
        display_name="TSV file with clade names",
        hidden=True,
    ),
    "string_species_list": LatchParameter(
        display_name="List of species names and identifiers", hidden=True
    ),
    "eukaryote_tree": LatchParameter(
        display_name="Tree of Eukaryotes in Newick format", hidden=True
    ),
}

FLOW = [
    Section(
        "Samples",
        Text(
            "Sample provided has to include an identifier for the sample (Sample name)"
            " and a LatchFile corresponding to a txt file with of all COGs of interest."
        ),
        Params("sample"),
    ),
    Section(
        "Species",
        Text(
            "You can either select one of the curated model species"
            " or provide a taxonomy identifier from NCBI for an eukaryote species"
            " (e.g. 9606 for Homo sapiens)."
        ),
        Fork(
            "species_fork",
            "Choose species",
            default=ForkBranch("Select from model species", Params("species")),
            manual=ForkBranch(
                "Use an NCBI taxonomy ID",
                Params("species_manual"),
            ),
        ),
    ),
    Section(
        "Auxiliary data files",
        Text(
            "Auxiliary data files from STRINGdb and other sources used as input for GenePlast."
        ),
        Params(
            "cog_mappings_file", "clade_names", "string_species_list", "eukaryote_tree"
        ),
    ),
]

geneplast_docs = LatchMetadata(
    display_name="GenePlast Eukaryote",
    documentation="https://github.com/jvfe/geneplast_latch/blob/main/README.md",
    author=LatchAuthor(
        name="jvfe",
        github="https://github.com/jvfe",
    ),
    repository="https://github.com/jvfe/geneplast_latch",
    license="MIT",
    parameters=PARAMS,
    tags=["rooting", "evolution"],
    flow=FLOW,
)
