#!usr/bin/env bash

# Process it into a more reasonable format
zcat COG_mappings_unprocessed.txt.gz \
 | awk 'NR > 1 { print gensub(/(^[0-9]+)(\.)(.*)/, "\\3\t\\1", "g", $1)"\t"$4}' \
 > cog_mappings.tsv