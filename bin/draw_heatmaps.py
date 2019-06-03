#! /usr/bin/env python

# coding: utf-8

# # Create a heatmap of taxa in all analysed samples, quantified by the number of reads per sample
# 
# _Date: 13 Nov 2018_  
# _Author: Sam Nooij_
# 
# Input: Identified taxa, number of reads (or read pairs) per taxon, total number of reads per sample
# 
# Output: Heatmap of taxa in different samples from the same run, quantified by their read numbers to look at the differences between samples
# 
# -- 14 Nov 2018 update: changed notebook into regular Python script that is run by the Snakefile
# -- 30 Apr 2019 update: start complete rework to make the script snakemake-independent and fix bugs
# 
# Required Python packages:
#  - Pandas
#  - Bokeh

# IMPORT required libraries--------------------------------
import argparse
import numpy as np
import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models import HoverTool, ColumnDataSource


# Set global VARIABLES-------------------------------------
RANKS = ["superkingdom", "phylum", "class", "order",
          "family", "genus", "species"]

PHAGE_FAMILY_LIST = ["Myoviridae", "Siphoviridae", "Podoviridae", "Lipothrixviridae", 
              "Rudiviridae", "Ampullaviridae", "Bicaudaviridae", "Clavaviridae", 
              "Corticoviridae", "Cystoviridae", "Fuselloviridae", "Globuloviridae", 
              "Guttaviridae", "Inoviridae", "Leviviridae", "Microviridae", 
              "Plasmaviridae", "Tectiviridae"]


# Define FUNCTIONS-----------------------------------------
def parse_arguments():
    """
    Parse the arguments from the command line, i.e.:
     -c/--classified = table with taxonomic classifications
     -n/--numbers = file with (MultiQC, Trimmomatic's) read numbers
     -s/--super = output file for superkingdoms heatmap
     -v/--virus = output files for virus heatmaps (as list)
     -p/--phage = output files for phage heatmaps (as list)
     -b/--bact = output files for bacteria heatmaps (as list)
     -sq/--super-quantities = output file for superkingdom quantities
     -st/--stats = output file with taxonomic rank statistics
     -vs/--vir-stats = ouput file for viral statistis
     -ps/--phage-stats = output file for phage statistics
     -bs/--bact-stats = output file for bacterial statistics
     -col/--colour = heatmap colour
     -h/--help = show help
    """
    parser = argparse.ArgumentParser(prog="draw heatmaps",
             description="Draw heatmaps for the Jovian taxonomic output",
             usage="draw_heatmaps.py -c -n -s -v -p -b -sq -st -vs -ps -bs -col"
             " [-h / --help]",
             add_help=False)

    required = parser.add_argument_group("Required arguments")

    required.add_argument('-c',
                          '--classified',
                          dest="classified",
                          metavar='',
                          required=True,
                          type=str,
                          help="Table with taxonomic classifications.")

    required.add_argument('-n',
                          '--numbers',
                          dest="numbers",
                          metavar='',
                          required=True,
                          type=str,
                          help="Multiqc Trimmomatic file with read numbers")

    required.add_argument('-sq',
                          '--super-quantities',
                          dest="super_quantities",
                          metavar='',
                          required=True,
                          type=str,
                          help="Table with superkingdom quantities per sample")

    required.add_argument('-st',
                          '--stats',
                          dest="stats",
                          metavar='',
                          required=True,
                          type=str,
                          help="Table with taxonomic rank statistics")

    required.add_argument('-vs',
                          '--vir-stats',
                          dest="vir_stats",
                          metavar='',
                          required=True,
                          type=str,
                          help="Table with virual taxonomic rank statistics")

    required.add_argument('-ps',
                          '--phage-stats',
                          dest="phage_stats",
                          metavar='',
                          required=True,
                          type=str,
                          help="Table with phage taxonomic rank statistics")

    required.add_argument('-bs',
                          '--bact-stats',
                          dest="bact_stats",
                          metavar='',
                          required=True,
                          type=str,
                          help="Table with bacterial taxonomic rank statistics")

    required.add_argument('-s',
                          '--super',
                          dest="super",
                          metavar='',
                          required=True,
                          type=str,
                          help="File name for superkingdoms heatmap")

    required.add_argument('-v',
                          '--virus',
                          dest="virus",
                          metavar='',
                          required=True,
                          type=str,
                          nargs='+',
                          help="Virus heatmap file name list")

    required.add_argument('-p',
                          '--phage',
                          dest="phage",
                          metavar='',
                          required=True,
                          type=str,
                          nargs='+',
                          help="Phage heatmap file name list")

    required.add_argument('-b',
                          '--bact',
                          dest="bact",
                          metavar='',
                          required=True,
                          type=str,
                          nargs='+',
                          help="Bacterium heatmap file names")

    optional = parser.add_argument_group("Optional arguments")

    optional.add_argument('-col',
                          '--colour',
                          dest="colour",
                          metavar='',
                          required=False,
                          type=str,
                          nargs='+',
                          default=[ "#000000" ],
                          help="Colour of the heatmap tiles")

    optional.add_argument('-h',
                          '--help',
                          action='help',
                          help="Show this message and exit.")  

    (args, extra_args) = parser.parse_known_args()

    return(args)


def read_numbers(infile):
    """
    Input: Tabular text file (.tsv) with number of reads/read pairs per sample
    Output: Pandas Dataframe with sample names and numbers in columns
    """
    # Read the number of read pairs per read set/sample
    numbers_df = pd.read_csv(infile, delimiter='\t')
    numbers_df = numbers_df[[ "Sample", "input_read_pairs" ]]
    numbers_df = numbers_df.rename(columns={"input_read_pairs" : "read_pairs"})

    numbers_df["Sample"] = numbers_df.Sample.apply(lambda x: x[:x.rfind("_R1")]) # On every value in column named "Sample" perform function that chops off "_R1" and any character after it
    
    return(numbers_df)


def read_classifications(infile):
    """
    Input: Tabulers text file (.tsv) with output from PZN analysis: 
      classifications for scaffolds and quantitative information of mapped-back reads,
      for _all samples analysed in the same run_
    Output: Pandas Dataframe with the information of the classified scaffolds
    """
    # Initialise the dataframe with taxonomic classifications
    # and numbers of reads mapped to the scaffolds (i.e.
    # the result/output of the pipeline).
    classifications_df = pd.read_csv(infile, delimiter='\t')

    # Check column names for debugging:
    #print(classifications_df.columns)

    # Select only relevant columns:
    classifications_df = classifications_df[[ "Sample_name", "scaffold_name", "taxID", 
                                             "tax_name", "superkingdom", 
                                             "kingdom", "phylum", "class", 
                                             "order", "family", "genus",
                                             "species", "Plus_reads", 
                                             "Minus_reads", "Avg_fold", "Length" 
                                            ]]

    # Calculate the number of read pairs matched to each scaffold
    # by averaging the plus and minus reads.
    # N.B. This is an imperfect approximation.
    classifications_df["reads"] = round((classifications_df.Plus_reads +
                                       classifications_df.Minus_reads) / 2 )
    
    return(classifications_df)


def filter_taxa(df, taxon, rank):
    """
    Filter taxa of interest of a certain rank from
    a dataframe.
    (taxon may be a single taxon as string, or a list of taxa)
    """
    if isinstance(taxon, str):
        # If a string is provided, continue as intended
        subset_df = df[df[rank] == taxon]
    elif isinstance(taxon, list) and len(taxon) == 1:
        # If a single-entry list is provided, use taxon as string
        taxon = taxon[0]
        subset_df = df[df[rank] == taxon]
    else:
        # If a list is provided, filter all given taxa
        taxa_list = taxon
        subset_df = df[df[rank].isin(taxa_list)]

    return(subset_df)


def remove_taxa(df, taxon, rank):
    """
    Negative filter of taxa of a certain rank from
    a dataframe: remove them and keep the rest.
    (taxon may be a single taxon as string, or a list of taxa)
    """
    if isinstance(taxon, str):
        # If a string is provided, continue as intended
        subset_df = df[~df[rank] == taxon]
    elif isinstance(taxon, list) and len(taxon) == 1:
        # If a single-entry list is provided, use taxon as string
        taxon = taxon[0]
        subset_df = df[~df[rank] == taxon]
    else:
        # If a list is provided, filter all given taxa
        taxa_list = taxon
        subset_df = df[~df[rank].isin(taxa_list)]

    return(subset_df)

def report_taxonomic_statistics(df, outfile):
    """
    Input: dataframe with classifications of scaffolds, a name for an output file (txt)
    Output: a list of statistics in a text file, like:
        superkingdom 4
        phylum 50
        class 99
        order 220
        family 373
        genus 649
        species 337
    """
    header="taxonomic_level\tnumber_found\n"
    with open(outfile, 'w') as f:
        f.write(header)
        # Count how many taxa have been reported
        for t in [ "superkingdom", "phylum", "class", "order", "family", "genus", "species" ]:
            f.write("%s\t%i\n" % (t, df[t].nunique()))
    
    print("File %s has been created!" % outfile)

    return(None)

def draw_heatmaps(df, outfile, title, taxonomic_rank, colour):
    """
    Draw heatmaps for the given input dataframe, to
    the specified file with the given title.
    """
    # If the sample contains only superkingdom information, use that:
    if taxonomic_rank == "superkingdom":
        #create source info
        #and set hovertool tooltip parameters
        samples = df["Sample_name"].astype(str)
        assigned = df["superkingdom"].astype(str)
        reads = df["reads"].astype(int)
        percent_of_total = df["Percentage"].astype(float)

        colors = len(reads) * colour #multiply to make an equally long list

        max_load = max(percent_of_total)
        alphas = [ min( x / float(max_load), 0.9) + 0.1 for x in percent_of_total ]

        source = ColumnDataSource(
            data = dict(samples=samples, assigned=assigned,
                        reads=reads, percent_of_total=percent_of_total, 
                        colors=colors, alphas=alphas)
        )

        y_value = (assigned, "assigned")
        
    # Otherwise, create the usual heatmap input info for each 
    # (relevant) taxonomic rank down to species.
    else:
        # Remove 'unclassified' taxa: NaN in dataframe
        df = df[df[taxonomic_rank].notnull()]

        # Check if the dataframe is empty
        if df.empty:
        # If so, warn the user and exit
            with open(outfile, 'w') as out:
                out.write("No contigs found for rank %s!\n" % taxonomic_rank)

            print("\n---\nThere are no contigs for the given %s. Heatmap %s could not be made.\n---\n" % (taxonomic_rank, outfile))

            return(None)

        else:
            #If it is not empty, continue normally

            samples = df["Sample_name"].astype(str)
            scaffolds = df["scaffold_name"].astype(str)
            assigned = df["tax_name"].astype(str)
            taxonomy = df[taxonomic_rank].astype(str)
            reads = df["reads"].astype(int)
            total_reads = df["read_pairs"].astype(int)
            percent_of_total = df["Percentage"].astype(float)
            coverage = df["Avg_fold"].astype(int)
            contig_length = df["Length"].astype(int)

            colors = len(reads) * colour #multiply to make an equally long list
            
            max_load = max(percent_of_total)
            alphas = [ min( x / float(max_load), 0.9) + 0.1 for x in percent_of_total ]
            
            source = ColumnDataSource(
                data = dict(samples=samples, scaffolds=scaffolds,
                            assigned=assigned, taxonomy=taxonomy,
                            reads=reads, total_reads=total_reads,
                            percent_of_total=percent_of_total, 
                            coverage=coverage,
                            contig_length=contig_length,
                            colors=colors, alphas=alphas)
            )

            y_value = (taxonomy, "taxonomy")

    TOOLS = "hover, save, pan, box_zoom, wheel_zoom, reset"

    p = figure(title = title,
                # If desired, the sample can be displayed as "Run x, sample y"
                # -> uncomment the next line
                #x_range = [ "Run %s, sample %s" % (x.split('_')[0], x.split('_')[1]) for x in list(sorted(set(samples))) ],
                x_range = list(sorted(set(df["Sample_name"]))),
                y_range = list(reversed(sorted(set(y_value[0])))), #reverse to order 'from top to bottom'
                x_axis_location = "above",
                toolbar_location="right",
                tools = TOOLS)

    # Edit the size of the heatmap when there are many samples and/or taxa
    if len(set(samples)) > 20:
        p.plot_width = int(len(set(samples)) * 25)
    else:
        pass
    # Adjust heatmap sizes depending on the number of 
    # taxa observed (not applicable for superkingdom heatmap)
    if taxonomic_rank != "superkingdom":
        if len(set(taxonomy)) > 100:
            p.plot_height = int(p.plot_height * 3)
            p.plot_width = int(p.plot_width * 1.5)
        elif len(set(taxonomy)) > 50:
            p.plot_height = int(p.plot_height * 2)
            p.plot_width = int(p.plot_width * 1.2)
        elif len(set(taxonomy)) > 25:
            p.plot_height = int(p.plot_height * 1.2)
        else:
            pass

        # And set tooltip depending on superkingdoms    
        p.select_one(HoverTool).tooltips = [
        ('Sample', "@samples"),
        ('Scaffold', "@scaffolds"),
        ('Taxon' , "@assigned"),
        ('Number of reads', "@reads (@percent_of_total % of sample total)"),
        ('Scaffold length', "@contig_length"),
        ('Average Depth of Coverage', "@coverage")
    ]
    else:
        p.select_one(HoverTool).tooltips = [
            ('Sample', "@samples"),
            ('Taxon' , "@assigned"),
            ('Number of reads', "@reads"),
            ('Percentage of total',  "@percent_of_total %")
        ]
    
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    if len(set(assigned)) > 15:
        p.axis.major_label_text_font_size = "10pt"
    else:
        p.axis.major_label_text_font_size = "12pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = np.pi/4
    p.title.text_color = colour[0]
    p.title.text_font_size = "16pt"
    p.title.align = 'right'

    p.rect("samples", y_value[1], 1, 1, source=source,
            color="colors", alpha="alphas", line_color=None)

    output_file(outfile, title=title)
    save(p)
    print("The heatmap %s has been created and written to: %s" % (title, outfile))

    return(None)


def main():
    """
    Main execution of the script
    """
    #1. Parse and show arguments
    arguments = parse_arguments()

    message =  ("\n"
                "These are the arguments you have provided:\n"
                "  INPUT:\n"
                "classified = {0},\n"
                "numbers = {1}\n"
                "  OUTPUT:\n"
                "super = {2}\n"
                "virus = {3}\n"
                "phage = {4}\n"
                "bact = {5}\n"
                "super_quantities = {6}\n"
                "stats = {7}\n"
                "vir_stats = {8}\n"
                "phage_stats = {9}\n"
                "bact_stats = {10}\n"
                "  OPTIONAL PARAMETERS:\n"
                "colour = {11}\n".format(arguments.classified,
                                        arguments.numbers,
                                        arguments.super,
                                        arguments.virus,
                                        arguments.phage,
                                        arguments.bact,
                                        arguments.super_quantities,
                                        arguments.stats,
                                        arguments.vir_stats,
                                        arguments.phage_stats,
                                        arguments.bact_stats,
                                        arguments.colour))

    print(message)
    
    #2. Read input files and make dataframes
    numbers_df = read_numbers(arguments.numbers)
    classifications_df = read_classifications(arguments.classified)

    merged_df = classifications_df.merge(numbers_df, left_on="Sample_name", right_on="Sample")
    merged_df["Percentage"] = merged_df.reads / merged_df.read_pairs * 100

    #3. Create chunks of information required for the heatmaps
    #3.1. Aggregate superkingdom-rank information
    # Count the percentages of Archaea, Bacteria, Eukaryota and Viruses per sample:
    superkingdom_sums = pd.DataFrame(merged_df.groupby(
                        [ "Sample_name", "superkingdom" ]).sum()
                        [[ "reads", "Percentage" ]])
    superkingdom_sums.reset_index(inplace=True) #to use MultiIndex "Sample_name" and "superkingdom" as columns
    
    missing_superkingdoms = { "Sample_name": [],
                            "superkingdom": [],
                            "reads": [],
                            "Percentage": []}
    
    # Check for missing taxa:
    for sample in set(superkingdom_sums["Sample_name"]):
        subset = superkingdom_sums.loc[superkingdom_sums.Sample_name == sample, ["superkingdom"]]
        for taxon in [ "Archaea", "Bacteria", "Eukaryota", "Viruses" ]:
            if taxon not in subset.values:
                missing_superkingdoms["Sample_name"].append(sample)
                missing_superkingdoms["superkingdom"].append(taxon)
                missing_superkingdoms["reads"].append(0)
                missing_superkingdoms["Percentage"].append(0)

    complete_superkingdoms = pd.concat([superkingdom_sums, pd.DataFrame(missing_superkingdoms)])
    complete_superkingdoms.sort_values(by=["Sample_name", "superkingdom"], inplace=True)
    complete_superkingdoms.reset_index(inplace=True)
    complete_superkingdoms["reads"] = complete_superkingdoms["reads"].astype(int)

    complete_superkingdoms.to_csv(arguments.super_quantities, index=False)
    print("File %s has been created!" % arguments.super_quantities)

    #3.2. Filter viruses from the table
    virus_df = filter_taxa(df=merged_df, taxon="Viruses", rank="superkingdom")
    # Remove the phages from the virus df to make less cluttered heatmaps
    virus_df = remove_taxa(df=virus_df, taxon=PHAGE_FAMILY_LIST, rank="family")
    
    #3.3. Filter phages
    phage_df = filter_taxa(df=merged_df, taxon=PHAGE_FAMILY_LIST, rank="family")

    #3.4. Filter bacteria
    bacterium_df = filter_taxa(df=merged_df, taxon="Bacteria", rank="superkingdom")

    #4. Write taxonomic rank statistics to a file, for each chunk
    #4.1. All taxa
    report_taxonomic_statistics(df = merged_df, outfile = arguments.stats)
    #4.2. Viruses
    report_taxonomic_statistics(df = virus_df, outfile = arguments.vir_stats)
    #4.3. Phages
    report_taxonomic_statistics(df = phage_df, outfile = arguments.phage_stats)
    #4.4. Bacteria
    report_taxonomic_statistics(df = bacterium_df, outfile = arguments.bact_stats)

    #5. Draw heatmaps for each chunk
    #5.1. All taxa: superkingdoms
    draw_heatmaps(df = complete_superkingdoms,
                  outfile=arguments.super, 
                  title="Superkingdoms heatmap", 
                  taxonomic_rank="superkingdom", 
                  colour = arguments.colour)

    #5.2. Viruses
    for rank in RANKS[3:]:
        # Create heatmaps for each rank below 'class'
        outfile_base = arguments.virus[0].split('.')[0]
        outfile_extension = arguments.virus[0].split('.')[1]
        outfile_new = outfile_base + "-%s." % rank + outfile_extension
        draw_heatmaps(df=virus_df,
                      outfile=outfile_new,
                      title="Virus %s heatmap" % rank,
                      taxonomic_rank=rank,
                      colour=arguments.colour)

    #5.3. Phages
    for rank in RANKS[3:]:
        # Create heatmaps for each rank below 'class'
        outfile_base = arguments.phage[0].split('.')[0]
        outfile_extension = arguments.phage[0].split('.')[1]
        outfile_new = outfile_base + "-%s." % rank + outfile_extension
        draw_heatmaps(df=phage_df,
                      outfile=outfile_new,
                      title="Phage %s heatmap" % rank,
                      taxonomic_rank=rank,
                      colour=arguments.colour)

    #5.4. Bacteria
    for rank in RANKS[1:]:
        # Create heatmaps for each rank below 'superkingdom'
        outfile_base = arguments.bact[0].split('.')[0]
        outfile_extension = arguments.bact[0].split('.')[1]
        outfile_new = outfile_base + "-%s." % rank + outfile_extension
        draw_heatmaps(df=bacterium_df,
                      outfile=outfile_new,
                      title="Bacterium %s heatmap" % rank,
                      taxonomic_rank=rank,
                      colour=arguments.colour)

#EXECUTE script--------------------------------------------
if __name__ == "__main__":
    main()