library(geneplast)
library(tibble)
library(dplyr)
library(vroom)
library(ape)
source("rotatePhyloTree.R")

set.seed(1024)

args <- commandArgs(trailingOnly = TRUE)

sample_name <- args[1]

# Make enum vs string
ref_species_id <- args[2]

cog_list <- args[3]

clade_names <- args[4]
string_species_list <- args[5]
eukaryote_tree <- args[6]

cog_data <- args[7]

result_file <- args[8]

# Read in auxiliary data files ----

lca_names <- vroom(clade_names)

string_eukaryotes <- vroom(string_species_list) %>%
  filter(domain == "Eukaryota") %>%
  select(ssp_id = `#taxon_id`,
         ssp_name = STRING_name_compact,
         domain = domain)

eukaryota_tree <- read.tree(eukaryote_tree) %>%
  rotatePhyloTree(ref_species_id) %>%
  purrr::list_modify(tip.alias = tibble::deframe(string_eukaryotes %>%
                                                   select(ssp_id, ssp_name))[.$tip.label])

cogs <- vroom(cog_data,
              col_names = c("protein_id", "ssp_id", "cog_id"),) %>%
  filter(ssp_id %in% string_eukaryotes$ssp_id)

gc()

cogs_of_interest <- readLines(cog_list) %>%
  as.data.frame() %>%
  setNames(c("cog_id"))

# Run geneplast ----

## Rooting ----

ogr_pre <- groot.preprocess(
  cogdata = as.data.frame(cogs),
  phyloTree = eukaryota_tree,
  spid = ref_species_id,
  cogids = cogs_of_interest,
  verbose = TRUE
)

ogr <- groot(ogr_pre, nPermutations = 100, verbose = TRUE)

### Write results ----

groot.get(ogr, what = "results") %>%
  tibble::rownames_to_column("cog_id") %>%
  select(cog_id, root = Root) %>%
  left_join(lca_names) %>%
  left_join(cogs_of_interest) %>%
  vroom_write(file = result_file)
