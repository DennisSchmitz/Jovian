
#@ # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#@ 
#@ 
#@ # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

rule Merge_all_metrics_into_single_tsv:
    input:
        bbtoolsFile                     =   rules.Generate_contigs_metrics.output.perScaffold,
        kronaFile                       =   rules.lca_mgkit.output.taxtab,
        minLenFiltScaffolds             =   rules.De_novo_assembly.output.filt_scaffolds,
        scaffoldORFcounts               =   rules.ORF_analysis.output.contig_ORF_count_list,
        virusHostDB                     =   config["databases"]["virusHostDB"],
        NCBI_new_taxdump_rankedlineage  =   config["databases"]["NCBI_new_taxdump_rankedlineage"],
        NCBI_new_taxdump_host           =   config["databases"]["NCBI_new_taxdump_host"],
    output:
        taxClassifiedTable      =   "data/tables/{sample}_taxClassified.tsv",
        taxUnclassifiedTable    =   "data/tables/{sample}_taxUnclassified.tsv",
        virusHostTable          =   "data/tables/{sample}_virusHost.tsv",
    conda:
        conda_envs + "data_wrangling.yaml"
    benchmark:
        "logs/benchmark/Merge_all_metrics_into_single_tsv_{sample}.txt"
    threads: 1
    log:
        "logs/Merge_all_metrics_into_single_tsv_{sample}.log"
    shell:
        """
python bin/scripts/merge_data.py {wildcards.sample} \
{input.bbtoolsFile} \
{input.kronaFile} \
{input.minLenFiltScaffolds} \
{input.scaffoldORFcounts} \
{input.virusHostDB} \
{input.NCBI_new_taxdump_rankedlineage} \
{input.NCBI_new_taxdump_host} \
{output.taxClassifiedTable} \
{output.taxUnclassifiedTable} \
{output.virusHostTable} > {log} 2>&1
        """