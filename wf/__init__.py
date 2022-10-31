import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from dataclasses_json import dataclass_json
from latch import medium_task, message, small_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchDir, LatchFile

from .docs import metadata


class Species(Enum):
    Homo_sapiens = "Homo sapiens"
    Mus_musculus = "Mus musculus"
    Drosophila_melanogaster = "Drosophila melanogaster"


@dataclass_json
@dataclass
class Sample:
    sample_name: str
    cog_list: LatchFile


def get_species_id(species_name):

    species_map = {
        "Homo sapiens": "9606",
        "Mus musculus": "10090",
        "Drosophila melanogaster": "7227",
    }

    return species_map[species_name]


@small_task
def get_cog_mappings(cog_mappings_file: str) -> LatchFile:
    """
    Get the mappings for COGs to STRINGdb IDs and process it into a readable file
    """
    db_file = "COG_mappings_unprocessed.txt.gz"
    db_filepath = Path(db_file).resolve()
    cog_mappings_name = "cog_mappings.tsv"
    cog_mappings_path = Path(cog_mappings_name).resolve()

    download_cmd = ["curl", "-L", cog_mappings_file, "-o", str(db_filepath)]

    message(
        "info",
        {
            "title": "Downloading COG mappings file",
            "body": f"Command string: {' '.join(download_cmd)}",
        },
    )
    subprocess.run(download_cmd, check=True)

    message("info", {"title": "Processing COG mappings file"})

    _process_cmd = [
        "bash",
        "process_mappings.sh"
    ]

    subprocess.run(_process_cmd)

    if cog_mappings_path.exists() == False:
        message(
            "error",
            {
                "title": "No output generated from the COG mappings file!",
                "body": "Check if the input file provided follows the same format as the example data file",
            },
        )

    return LatchFile(str(cog_mappings_path), f"latch:///GenePlast/{cog_mappings_name}")


@medium_task
def run_geneplast(
    sample: Sample,
    clade_names: LatchFile,
    string_species_list: LatchFile,
    eukaryote_tree: LatchFile,
    cog_mappings: LatchFile,
    species: Species = Species.Homo_sapiens,
) -> LatchFile:
    """
    Run the GenePlast analysis pipeline, outputting a tsv file with roots for the COGs provided
    """
    sample_name = sample.sample_name
    species_id = get_species_id(species.value)
    output_file = f"{sample_name}_roots.tsv"
    output_filepath = Path(output_file).resolve()

    _geneplast_cmd = [
        "Rscript",
        "/root/geneplast_eukaryote.R",
        sample_name,
        species_id,
        sample.cog_list.local_path,
        clade_names.local_path,
        string_species_list.local_path,
        eukaryote_tree.local_path,
        cog_mappings.local_path,
    ]

    message(
        "info",
        {
            "title": "Running GenePlast",
            "body": f"Running GenePlast. Command string: {' '.join(_geneplast_cmd)}",
        },
    )

    subprocess.run(
        _geneplast_cmd,
        check=True,
    )

    if output_filepath.exists() == False:
        message(
            "error",
            {
                "title": "No output generated from GenePlast!",
                "body": "GenePlast ran but no output was generated. Check if input files are valid.",
            },
        )

    return LatchFile(str(output_filepath), f"latch:///GenePlast/{output_filepath}")


@workflow(metadata)
def geneplast(
    sample: Sample,
    species: Species,
    clade_names: LatchFile,
    string_species_list: LatchFile,
    eukaryote_tree: LatchFile,
    cog_mappings_file: str,
) -> LatchFile:
    """Evolutionary rooting of orthologous groups

    GenePlast
    ----

    Geneplast[^1] is designed for evolutionary and plasticity analysis
    based on orthologous groups distribution in a given species tree.
    It implements the Bridge algorithm to determine the evolutionary
    root of a given gene based on its orthologs distribution.

    Read more about it
    [here](http://bioconductor.org/packages/release/bioc/vignettes/geneplast/inst/doc/geneplast.html)

    [^1]: Dalmolin, JS R, Castro, AA M (2015). Geneplast: evolutionary
    rooting and plasticity inference. R package.
    """

    cog_mappings = get_cog_mappings(cog_mappings_file=cog_mappings_file)

    return run_geneplast(
        sample=sample,
        species=species,
        clade_names=clade_names,
        string_species_list=string_species_list,
        eukaryote_tree=eukaryote_tree,
        cog_mappings=cog_mappings,
    )


LaunchPlan(
    geneplast,
    "Default protein data",
    {
        "sample": Sample(
            sample_name="default_proteins",
            cog_list=LatchFile("s3://latch-public/test-data/4318/cog_list.txt"),
        ),
        "species": Species.Homo_sapiens,
        "clade_names": LatchFile(
            "s3://latch-public/test-data/4318/geneplast_clade_names.tsv"
        ),
        "string_species_list": LatchFile(
            "s3://latch-public/test-data/4318/species.v11.5.txt"
        ),
        "eukaryote_tree": LatchFile(
            "s3://latch-public/test-data/4318/hybrid_tree_modified.nwk"
        ),
        "cog_mappings_file": "https://stringdb-static.org/download/COG.mappings.v11.5.txt.gz",
    },
)
