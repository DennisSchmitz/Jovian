
#@ # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#@ 
#@ 
#@ # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

rule Determine_GC_content:
    input:
        fasta       =   rules.De_novo_assembly.output.filt_scaffolds,
        fasta_fai   =   rules.SNP_calling.output.fasta_fai
    output:
        fasta_sizes =   "data/scaffolds_filtered/{sample}_scaffolds_ge%snt.fasta.sizes" % config["Illumina_meta"]["minlen"],
        bed_windows =   "data/scaffolds_filtered/{sample}.windows",
        GC_bed      =   "data/scaffolds_filtered/{sample}_GC.bedgraph"
    conda:
        conda_envs + "Sequence_analysis.yaml"
    log:
        "logs/Determine_GC_content_{sample}.log"
    benchmark:
        "logs/benchmark/Determine_GC_content_{sample}.txt"
    threads: 1
    params:
        window_size =   config["Global"]["GC_window_size"]
    shell:
        """
cut -f 1,2 {input.fasta_fai} 2> {log} 1> {output.fasta_sizes}
bedtools makewindows \
-g {output.fasta_sizes} \
-w {params.window_size} 2>> {log} 1> {output.bed_windows}
bedtools nuc \
-fi {input.fasta} \
-bed {output.bed_windows} 2>> {log} |\
cut -f 1-3,5 2>> {log} 1> {output.GC_bed}
        """