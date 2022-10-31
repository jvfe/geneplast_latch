from latch.types import LatchAuthor, LatchMetadata, LatchParameter

metadata = LatchMetadata(
    display_name="GenePlast Eukaryote",
    documentation="https://github.com/jvfe/geneplast_latch/blob/main/README.md",
    author=LatchAuthor(
        name="jvfe",
        github="https://github.com/jvfe",
    ),
    repository="https://github.com/jvfe/geneplast_latch",
    license="MIT",
)

metadata.parameters = {
    "sample": LatchParameter(
        display_name="Sample name",
        section_title="Protein Lists",
        description="Dataset from which to estimate evolutionary roots.",
    ),
    "species": LatchParameter(
        display_name="Reference species for the rooting analysis",
    ),
    "cog_mappings_file": LatchParameter(
        display_name="URL to a STRINGdb COG mappings file",
        section_title="Auxiliary data files",
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
