# Jovian, user-friendly metagenomics     

**IMPORTANT: Do not share the code without my express permission as it is unpublished (manuscript in preparation)**  

___

<img align="right" src="../assets/images/Jovian_logo.png">

## Table of content  
- [Pipeline description](#pipeline-description)  
  - [Pipeline features](#pipeline-features)  
  - [Pipeline visualizations](#pipeline-visualizations)  
  - [Virus typing](#virus-typing)  
  - [Audit trail](#audit-trail)  
- [Pipeline requirements](#pipeline-requirements)  
  - [Software](#software)  
  - [Databases](#databases)  
- [Configuration](#configuration)  
  - [Installing the pipeline](#installing-the-pipeline)  
  - [Database configuration](#database-configuration)  
  - [Setup Jupyter Notebook user profile](#setup-jupyter-notebook-user-profile)  
  - [Starting the Jupyter Notebook server process](#starting-the-jupyter-notebook-server-process)  
  - [Configuration for remote and grid computers](#configuration-for-remote-and-grid-computers)  
- [How to start a Jovian analysis](#how-to-start-a-jovian-analysis)  
- [Explanation of output folders](#explanation-of-output-folders)  
- [FAQ](#faq)  
- [Example Jovian report](#example-jovian-report)  
- [Acknowledgements](#acknowledgements)  
- [Authors](#authors)  

___

## Pipeline description  

The pipeline automatically processes raw Illumina NGS data from human clinical matrices (faeces, serum, etc.) into clinically relevant information such as taxonomic classification, viral typing and minority variant identification (quasispecies).
Wetlab personnel can start, configure and interpret results via an interactive web-report. This makes doing metagenomics analyses much more accessible and user-friendly since minimal command-line skills are required.  

### Pipeline features    
- Data quality control (QC) and cleaning.  
  - Including library fragment length analysis, usefull for sample preparation QC.  
- Removal of human* data (patient privacy).  
  - _* You can use whichever reference you would like, as [explained here](#faq). However, since Jovian is intended for human clinical samples, we suggest using a human reference._  
- Assembly of short reads into bigger scaffolds (often full viral genomes).  
- Taxonomic classification:  
  - Every nucleic acid containing biological entity (i.e. not only viruses) is determined up to species level.  
  - Lowest Common Ancestor (LCA) analysis is performed to move ambiguous results up to their last common ancestor, which makes results more robust.  
- Viral typing:
  - Several viral families and genera can be taxonomically labelled at the sub-species level as described [here](#virus-typing).  
- Viral scaffolds are cross-referenced against the Virus-Host interaction database and NCBI host database.  
- Scaffolds are detailedly annotated:  
  - Depth of coverage.  
  - GC content.  
  - Open reading frames (ORFs) are predicted.  
  - Minority variants (quasispecies) are identified.  
- Importantly, results of all processes listed above are presented via an [interactive web-report](#pipeline-visualizations) which includes an [audit trail](#audit-trail).  

### Pipeline visualizations  
All data are visualized via an interactive web-report, [as shown here](#example-jovian-report), which includes:  
- A collation of interactive QC graphs via `MultiQC`.  
- Taxonomic results are presented on three levels:  
  - For an entire (multi sample) run, interactive heatmaps are made for non-phage viruses, phages and bacteria. They are stratified to different taxonomic levels.  
  - For a sample level overview, `Krona` interactive taxonomic piecharts are generated.  
  - For more detailed analyses, interactive tables are included. Similar to popular spreadsheet applications (e.g. Microsoft Excel).  
    - Classified scaffolds  
    - Unclassified scaffolds (i.e. "Dark Matter")  
- Virus typing results are presented via interactive spreadsheet-like tables.  
- An interactive scaffold alignment viewer (`IGVjs`) is included, containing:  
  - Detailed alignment information.  
  - Depth of coverage graph.  
  - GC content graph.
  - Predicted open reading frames (ORFs).  
  - Identified minority variants (quasispecies).  
- All SNP metrics are presented via interactive spreadsheet-like tables, allowing detailed analysis.  

### Virus typing
After a Jovian analysis is finished you can perform virus-typing (i.e. sub-species level taxonomic labelling). These analyses can be started by the command `bash jovian -vt [virus keyword]`, where `[virus keyword]` can be: `NoV` (Caliciviridae), `EV` (Picornaviridae), `RVA` (_Rotavirus A_), `HAV` (_Hepatovirus A | Hepatitis A_), `HEV` (_Orthohepevirus A | Hepatitis E_), `PV` (Papillomaviridae) or `Flavi` (Flaviviridae). More detailed information is given upon the command `bash jovian -vt-help`.  
  
### Audit trail  
An audit trail, used for clinical reproducability and logging, is generated and contains:  
- A unique methodological fingerprint of the code is generated and accessible via GitHub: allowing to exactly reproduce the analysis, even retrospectively by reverting to old versions of the pipeline code.  
- The following information is also logged:  
  - Database timestamps  
  - (user-specified) Pipeline parameters  

However, several things are out-of-scope for Jovian logging:
- The `IGVjs` version  
- The `virus typing-tools` version  
  - Currently we depend on a public web-tool hosted by the [RIVM](https://www.rivm.nl/en). These are developed in close collaboration with - *but independently of* - Jovian. A versioning system for the `virus typing-tools` is being worked on, however, this is not trivial and will take some time.  
- The database versions  
  - We only save the timestamps of the database files, this is because the databases used by Jovian have no official versioning. Any versioning scheme is therefore out-of-scope for Jovian and a responsibility of the end-user.  
- Input files
  - We only save the names and location of input files at the time the analysis was performed. Long-term storage of the data, and documenting their location over time, is the responsibility of the end-user.  

___

![Jovian_rulegraph.png](../assets/images/rulegraph_Jovian.png?raw=true)
___

## Pipeline requirements
Jovian has two major software dependencies, miniConda and IGVjs. On first usage, you will be asked if you want to automatically install these. It also depends on the [following software](#software), but most systems will have these installed already. An analysis also depends on several databases that you have to download yourself, as [described below](#databases). And it requires some configuration, as explained [here](#configuration).  

### System rights
In order to run Jovian there are very little additional system rights necessary, Root and/or sudo-rights are not required.  
It is however necessary to have read and write access to the `/tmp` folder on your system. This won't be a problem most of the time since the `/tmp` folder is usually free to read from and write to. However, it is best to check this with your system administrator(s).

### Software  
|Software name|Website|  
|:---|:---|  
|`git`| https://git-scm.com/downloads |  
|`curl`| https://curl.haxx.se/ |  
|`which`| http://savannah.gnu.org/projects/which |  
|`bzip2`| http://www.bzip.org/ |  

### Databases  
|Database name|Link|Installation instructions|
|:---|:---|:---|
|`NCBI NT & NR`| ftp://ftp.ncbi.nlm.nih.gov/blast/db/ | [link](#blast-nt-nr-and-taxdb-databases)|
|`NCBI Taxdump`| ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/ | [link](#blast-nt-nr-and-taxdb-databases)|
|`NCBI New_taxdump`| ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/new_taxdump/ | [link](#ncbi-new_taxdump-database)|
|`Latest Human Genome`*| https://support.illumina.com/sequencing/sequencing_software/igenome.html | [link](#human-genome)|
|`Virus-Host interaction database`| http://www.genome.jp/virushostdb/note.html | [link](#virus-host-interaction-database)|

_* We suggest the latest human genome because Jovian is intended for clinical samples. You can however use any reference you'd like, as [explained here](#faq)._

___

## Configuration  
Pipeline software, databases and Jupyter Notebook need to be downloaded, installed and configured as described below.  

### Installing the pipeline  
- Installing the Jovian pipeline requires a specific file (.ncbirc) in your home directory, you can create this file with the command `touch ~/.ncbirc`
    - This file (.ncbirc) **needs** to be updated later on with information regarding your local setup in order to make the pipeline actually work.
- Navigate to a directory where you want to analyse your datasets and download the pipeline via `git clone https://github.com/DennisSchmitz/Jovian.git`  
- Navigate to the newly created `Jovian` folder.
- Depending on your local setup, you need to modify the config files in order to make the pipeline work as intended.
    - **[For grid-computing setups]** Open the file `profile/config.yaml` with your text-editor of choice and modify the amount of cores to match your setup. It is also important to update the DRMAA queue information to match your setup. If this is unknown, contact your local system administrator(s) for more information.
    - **[For standalone-computing setups]** Open the file `profile/config.yaml` with your text-editor of choice and modify the amount of cores to something acceptable for your setup. (depending on your dataset and server, 8 to 12 cores should be fine). Then comment out the lines starting with "drmaa", this can be done by placing a "#" in front of the line as in the example below: 
    ```
    #drmaa: " -q bio -n {threads} -R \"span[hosts=1]\""
    #drmaa-log-dir: logs/drmaa
    ```
- Now run `bash jovian -ic` to begin the interactive installer for jovian (make sure you run this command while in the `Jovian` folder)
    - This command will install all files, folders and programs necessary for Jovian, it will however only do so if you give consent to do so. Once done with the installation it will go on with building different "environments" which are necessary for analysing the data.
- Follow the instructions on screen and answer the questions given in order to completely install Jovian. Installation can take roughly up to an hour or two (depending on your system). It is only necessary to stay with your computer during the interactive installer which won't take longer than 30 minutes.
    - If you're inexperienced with the commandline, it is best to simply answer all questions in the interactive installer with "yes"  or "y". 

#### Installing IGVjs
The installation of IGVjs is usually handled by the interactive Jovian installer (described above).  
In case the installation of IGVjs is declined during installation and you wish to install/use IGVjs at a moment of your convenience, run the following command:  
`bash jovian -ii`  
The installation of IGVjs will now start, this can take up to 30 minutes.

### Database configuration  
**N.B. These databases should be updated simulatenously, otherwise the taxonomy IDs might not be valid.**  

#### BLAST NT, NR and taxdb databases  
- Use the `Jovian_helper` environment, i.e. `conda activate Jovian_helper`.  
- Use the script to download...  
  - NT: `cd [desired_database_location]; perl ${CONDA_PREFIX}/bin/update_blastdb.pl --decompress nt`  
  - NR: `cd [desired_database_location]; perl ${CONDA_PREFIX}/bin/update_blastdb.pl --decompress nr`  
  - Taxdb: `cd [desired_database_location]; perl ${CONDA_PREFIX}/bin/update_blastdb.pl --decompress taxdb`  
- Put a file named [.ncbirc](files/.ncbirc) in your home (`cd ~`) directory. See this example [.ncbirc](files/.ncbirc), remember to update it for your local setup!   
  - We advise you to setup automatic `crontab` scripts to update these databases every week, please contact your own IT support for help with this.  

#### NCBI new_taxdump database  
This section is work in progress, will be automated in the bash wrapper, see issue #7.  
- Download `new_taxdump` from https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/new_taxdump/   
- Extract it, it should contain the `rankedlineage` and `host` files.
- Then change the delimiters via this one liner:
 **N.B. execute this command from the directory where these `*.dmp` files are located**  
 `for file in *.dmp; do awk '{gsub("\t",""); if(substr($0,length($0),length($0))=="|") print substr($0,0,length($0)-1); else print $0}' < ${file} > ${file}.delim; done`  
- When you run a Jovian analysis, update the pathing information in [profile/pipeline_parameters.yaml](profile/pipeline_parameters.yaml) to your local pathing.  

#### Krona resources  
- Use the `Jovian_helper` environment, i.e. `conda activate Jovian_helper`.  
- Use the code below to generate the Krona taxonomy files:  
  ```cd [desired_database_location]; bash ${CONDA_PREFIX}/opt/krona/updateTaxonomy.sh ./ ; bash ${CONDA_PREFIX}/opt/krona/updateAccessions.sh ./```  
- When you run a Jovian analysis, update the pathing information to the Krona resources in [profile/pipeline_parameters.yaml](profile/pipeline_parameters.yaml) to your local pathing.  

#### Human Genome  
_We suggest the latest human genome because Jovian is intended for clinical samples. You can however use any reference you'd like, as [explained here](#faq)._
- Download the latest Human Genome version from https://support.illumina.com/sequencing/sequencing_software/igenome.html  
  - Select the NCBI version of `GRCh38`. NB do NOT download the `GRCh38Decoy` version! This version will filter out certain human viruses.  
- The `GRCh38` version of the human genome still contains an Epstein Barr virus (EBV) contig, this needs to be removed as shown below:  
  - Navigate to `NCBI/GRCh38/Sequence/Bowtie2Index/` in the newly downloaded Human Genome.  
  - Remove the EBV contig via `awk '{print >out}; />chrEBV/{out="EBV.fa"}' out=nonEBV.fa genome.fa` ([source](https://unix.stackexchange.com/questions/202514/split-file-into-two-parts-at-a-pattern)).  
  - Remove `EBV.fa` and replace `genome.fa` with `nonEBV.fa` via `rm EBV.fa; mv nonEBV.fa genome.fa`  
  - Activate the `Jovian_helper` environment via `source activate Jovian_helper` and index the updated `genome.fa` file via `bowtie2-build --threads 10 genome.fa genome.fa`.  
- When you run a Jovian analysis, update the pathing information to your cleaned and bowtie2 indexed `genome.fa` file in [profile/pipeline_parameters.yaml](profile/pipeline_parameters.yaml).  

#### Virus-Host interaction database  
- Download the Virus-Host database (Mihara et al. 2016) via...  
  - ```cd [desired_database_location]; wget ftp://ftp.genome.jp/pub/db/virushostdb/virushostdb.tsv```  
- When you run a Jovian analysis, update the pathing information to the Virus-Host interaction table in [profile/pipeline_parameters.yaml](profile/pipeline_parameters.yaml) to your local pathing.  

### Setup Jupyter Notebook user profile  
Run `jovian --configure-jupyter` and when it asks about overwriting default config reply `y` and press `enter`.  

### Starting the Jupyter Notebook server process  
- Open a Linux terminal and navigate to the root via `cd /`  
- Start the Jupyter Notebook server via `jupyter notebook`. NB Keep this proces runnning for as long as you want to access these Jupyter Notebooks Reports.  
- The above command should give your a link that you can access via your browser, please open this link from your work station. If you cannot find this link, you can run `jupyter notebook list` from a seperate terminal to generate it.  

### Configuration for remote and grid computers
- If you run the pipeline on a remote computer (e.g. server/HPC or grid) you need the system admins of those systems to make Jupyter Notebook accessible to your local computer. 
  
___
 
## How to start a Jovian analysis  
Currently, the method to launch analyses via the Jupyter Notebook requires some minor tweaks. So I cannot share it yet, we recommend you to use the command-line method below.  

<b>Jupyter Notebook method:</b>  
- Via your Jupyter Notebook browser connection, go to the `Jovian` folder [created above](#installing-the-pipeline). Then, open `Notebook_portal.ipynb`.  
- Follow the instructions in this notebook to start an analysis.  

<b>Command-line interface method:</b>  
- Make sure the installation of Jovian is completed, see: [installing the pipeline](#installing-the-pipeline)
- Go to the `Jovian` folder [created above](#installing-the-pipeline)
- Configure pipeline parameters by changing the [profile/pipeline_parameters.yaml](profile/pipeline_parameters.yaml) file. Either via Jupyter Notebook or with a commandline text-editor of choice.  
- We recommended you do a `dry-run` before each analysis to check if there are any typo's, missing files or other errors. This can be done via `bash jovian -i <input_directory> -n`
- If the dry-run has completed without errors, you are ready to start a real analysis with the following command:  
`bash jovian -i <input_directory>` 
- After the pipeline has finished, open `Notebook_report.ipynb` via your browser. Click on `Cell` in the toolbar, then press `Run all` and wait for data to be imported.  
  - N.B. You need to have a Jupyter notebook process running in the background, as described [here](#starting-the-jupyter-notebook-server-process); i.e. `jupyter notebook`.  

_____

## Explanation of output folders  
|Folder|Contents|
|:---|:---|
|`bin/` |Contains the scripts required for Jovian to work |
|`data/` | Contains intermediate and detailed data |
|`envs/` | Contains all conda environments for the pipeline |
|`files/` | Contains ancillary files for the pipeline |
|`logs/` | Contains all Jovian log files, use these files to troubleshoot errors |
|`profile/` | Contains the files with Snakemake and pipeline parameters |
|`results/` | This contains all files that are important for end-users and are imported by the Jupyter Report |

Also, a hidden folder named `.snakemake` is generated. Do not remove or edit this folder. Jovian was built via `Snakemake` and this folder contains all the software and file-metadata required for proper pipeline functionality.  
___

## FAQ
- _I get an error saying the directory is locked, what should I do?_
  - Probably an earlier analysis crashed and/or was cancelled by the user while the pipeline was still running. You can unlock the directory by typing `bash jovian --unlock`.  
- _Why are there multiple lines per taxid in the host table?_  
  - In the Virus-Host interaction database there are sometimes multiple entries for a single taxid, meaning, there are multiple known hosts. Therefore, we follow this formatting and print the different hosts on multiple lines.  
- _Why doesn't the virus typing-tool accept my query?_
  - Please see [this](https://github.com/DennisSchmitz/Jovian/issues/29) and [this](https://github.com/DennisSchmitz/Jovian/issues/51) issue. The short answer; they were made for Sanger sequences and are not yet able to to handle NGS datasets. This is a work-in-progress.  
- _I am missing a certain taxa of which I'm sure is in the dataset. How is that possible?_
  - Could be due to multiple reasons. The first one being the stringency of the analysis. The current default values are quite strict, you might have filtered it away. Please try more relaxed settings. The second being the result of the LCA analysis (Lowest Common Ancestor) putting a certain scaffold at a unexpected taxonomic level. Imagine a sequence that is homologous between (pro)phages and bacteria, the lowest common ancestor between phages and bacteria is the theoretical root of all life (i.e. `root` taxonomic level), so you will find it at the taxonomic level (you can try changing the `bitscoreDeltaLCA: 5` to `0` in the [config-file](profile/pipeline_parameters.yaml). It could also be a result of an erroneous entry in the used public databases, to which a scaffold then gets assigned. If it is anything other than these reasons, please let us know by making an [issue](https://github.com/DennisSchmitz/Jovian/issues).  
- _I don't care about removing the human data, I have cell-lines which are from other species, can I also automatically remove that?_
  - Yes. Although we focus on patient-privacy since it was developed for clinical samples, you can enter any reference sequence you like. You can do that by changing `background_ref: /path/to/file/genome.fa` into the location of your desired background removal organisms in the [config-file](profile/pipeline_parameters.yaml). The only limitations are that it is a `fasta` file and that is indexed via `bowtie2`, although this latter process will be automated in a future version.  
- _How can some scaffolds still be assigned to `Homo sapiens`? I thought Jovian removed human data?_
  - The human genome is a consensus genome built from many individuals from around the globe. It does not capture all diversity in the human gene pool and therefore cannot completely remove all human data. You can improve this by selecting a reference genome that is closer to your target population, e.g. if you sequence mainly Dutch samples, the [GoNL genome](http://www.nlgenome.nl/) might be better suited.  

___

## Example Jovian report  
_Data shown below is based on public data, available on ENA via accession ID `PRJNA491626`. It contains Illumina paired-end data of faeces from people with gastroenteritis._  

**MultiQC is used to summarize many pipeline metrics, including read quality, insert-size distribution, biases, etc.:**  
<br>
![Jovian_QC-report_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_QC-report_PRJNA491626-public-dataset.PNG?raw=true)

**A summary barchart overview of the entire dataset is also presented:**
<br>
![Jovian_barcharts_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_barcharts_PRJNA491626-public-dataset.PNG?raw=true)

**Metagenomics data is presented through three different visualizations, Krona pie-charts give sample level overview:**  
<br>
![Jovian_Krona-chart_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_Krona-chart_PRJNA491626-public-dataset.PNG?raw=true)

**Viral and bacterial heatmaps that are stratified to different taxonomic levels give an overview of the complete dataset:**  
<br>
![Jovian_heatmap_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_heatmap_PRJNA491626-public-dataset.png?raw=true)

**All classified scaffolds and their metrics are presented through interactive tables that are functionally similar to popular spreadsheet programs. Allowing filtering for certain metrics, e.g. taxonomic level (species up to superkingdom), length, number of ORFs, percentage GC, depth of coverage, etc. to facilitate in-depth analyses:**
<br>
![Jovian_classified-scaffolds_PRJNA491626-public-dataset.png](../assets/images/screenshots/Jovian_classified-scaffolds_PRJNA491626-public-dataset.png?raw=true)

**Any scaffold that could not be classified ("dark matter") is reported in a similar interactive table for further investigation:**
<br>
![Jovian_dark-matter_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_dark-matter_PRJNA491626-public-dataset.PNG?raw=true)

**All classified scaffolds are also cross-referenced against the NCBI host information and the Virus-Host database:**
<br>
![Jovian_host-disease_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_host-disease_PRJNA491626-public-dataset.PNG?raw=true)

**The typing-tool output for Caliciviridae, Picornaviridae, Hepatoviruses, Orthohepeviruses and Rotaviruses containing the genotype information are also presented:**
<br>
![Jovian_NoV-TT_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_NoV-TT_PRJNA491626-public-dataset.PNG?raw=true)
![Jovian_EV-TT_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_EV-TT_PRJNA491626-public-dataset.PNG?raw=true)
![Jovian_HAV-TT_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_HAV-TT_PRJNA491626-public-dataset.PNG?raw=true)
![Jovian_RVA-TT_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_RVA-TT_PRJNA491626-public-dataset.PNG?raw=true)

**IGVjs is used to visualize genomes, you can zoom in to individual sites to inspect e.g. minority variants in greater detail. It incorporates and shows the depth of coverage, GC contents, predicted ORFs, minority variants (quasispecies) alongside each individual aligning read:**  
<br>
![Jovian_IGVjs_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_IGVjs_PRJNA491626-public-dataset.PNG?raw=true)
![Jovian_IGVjs-zoom_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_IGVjs-zoom_PRJNA491626-public-dataset.PNG?raw=true)

**The SNP information is also presented through a spreadsheet table for filtering and in-depth analysis:**  
<br>
![Jovian_minority-SNP-table_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_minority-SNP-table_PRJNA491626-public-dataset.PNG?raw=true)

**Lastly, the logging of software, databases and pipeline settings are presented to the user. A verbose list containing all software in the current running environment, `Jovian_master`, is reported (not shown). Also, a list containing the timestamps of all used databases are reported (not shown). Via Snakemake a report is created describing exactly what software and which versions were used (shown below), alongside information about how long each step in the pipeline took to complete (not shown). The Git hash is reported, the unique Jovian methodological "fingerprint", which allows exact reproduction of results at a later time (shown below). And pipeline settings for the current analysis are reported (shown below):**  
<br>
![Jovian_Snakemake-report_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_Snakemake-report_PRJNA491626-public-dataset.PNG?raw=true)
![Jovian_logging-git-hash-config_PRJNA491626-public-dataset.PNG](../assets/images/screenshots/Jovian_logging-git-hash-config_PRJNA491626-public-dataset.PNG?raw=true)

___

## Acknowledgements

|Name |Publication|Website|
|:---|:---|:---|
|`BBtools`|NA|https://jgi.doe.gov/data-and-tools/bbtools/|
|`BEDtools`|Quinlan, A.R. and I.M.J.B. Hall, BEDTools: a flexible suite of utilities for comparing genomic features. 2010. 26(6): p. 841-842.|https://bedtools.readthedocs.io/en/latest/|
|`BLAST`|Altschul, S.F., et al., Gapped BLAST and PSI-BLAST: a new generation of protein database search programs. 1997. 25(17): p. 3389-3402.|https://www.ncbi.nlm.nih.gov/books/NBK279690/|
|`BWA`|Li, H. (2013). Aligning sequence reads, clone sequences and assembly contigs with BWA-MEM. arXiv preprint arXiv:1303.3997.|https://github.com/lh3/bwa|
|`BioConda`|Grüning, B., et al., Bioconda: sustainable and comprehensive software distribution for the life sciences. 2018. 15(7): p. 475.|https://bioconda.github.io/|
|`Biopython`|Cock, P. J., Antao, T., Chang, J. T., Chapman, B. A., Cox, C. J., Dalke, A., ... & De Hoon, M. J. (2009). Biopython: freely available Python tools for computational molecular biology and bioinformatics. Bioinformatics, 25(11), 1422-1423.|https://biopython.org/|
|`Bokeh`|Bokeh Development Team (2018). Bokeh: Python library for interactive visualization.|https://bokeh.pydata.org/en/latest/|
|`Bowtie2`|Langmead, B. and S.L.J.N.m. Salzberg, Fast gapped-read alignment with Bowtie 2. 2012. 9(4): p. 357.|http://bowtie-bio.sourceforge.net/bowtie2/index.shtml|
|`Conda`|NA|https://conda.io/|
|`DRMAA`|NA|http://drmaa-python.github.io/|
|`FastQC`|Andrews, S., FastQC: a quality control tool for high throughput sequence data. 2010.|https://www.bioinformatics.babraham.ac.uk/projects/fastqc/|
|`gawk`|NA|https://www.gnu.org/software/gawk/|
|`GNU Parallel`|O. Tange (2018): GNU Parallel 2018, March 2018, https://doi.org/10.5281/zenodo.1146014.|https://www.gnu.org/software/parallel/|
|`Git`|NA|https://git-scm.com/|
|`igvtools`|NA|https://software.broadinstitute.org/software/igv/igvtools|
|`Jupyter Notebook`|Kluyver, Thomas, et al. "Jupyter Notebooks-a publishing format for reproducible computational workflows." ELPUB. 2016.|https://jupyter.org/|
|`Jupyter_contrib_nbextension`|NA|https://github.com/ipython-contrib/jupyter_contrib_nbextensions|
|`Jupyterthemes`|NA|https://github.com/dunovank/jupyter-themes|
|`Krona`|Ondov, B.D., N.H. Bergman, and A.M. Phillippy, Interactive metagenomic visualization in a Web browser. BMC Bioinformatics, 2011. 12: p. 385.|https://github.com/marbl/Krona/wiki|
|`Lofreq`|Wilm, A., et al., LoFreq: a sequence-quality aware, ultra-sensitive variant caller for uncovering cell-population heterogeneity from high-throughput sequencing datasets. 2012. 40(22): p. 11189-11201.|http://csb5.github.io/lofreq/|
|`Minimap2`|Li, H., Minimap2: pairwise alignment for nucleotide sequences. Bioinformatics, 2018.|https://github.com/lh3/minimap2|
|`MultiQC`|Ewels, P., et al., MultiQC: summarize analysis results for multiple tools and samples in a single report. 2016. 32(19): p. 3047-3048.|https://multiqc.info/|
|`Nb_conda`|NA|https://github.com/Anaconda-Platform/nb_conda|
|`Nb_conda_kernels`|NA|https://github.com/Anaconda-Platform/nb_conda_kernels|
|`Nginx`|NA|https://www.nginx.com/|
|`Numpy`|Walt, S. V. D., Colbert, S. C., & Varoquaux, G. (2011). The NumPy array: a structure for efficient numerical computation. Computing in Science & Engineering, 13(2), 22-30.|http://www.numpy.org/|
|`Pandas`|McKinney, W. Data structures for statistical computing in python. in Proceedings of the 9th Python in Science Conference. 2010. Austin, TX.|https://pandas.pydata.org/|
|`Picard`|NA|https://broadinstitute.github.io/picard/|
|`Prodigal`|Hyatt, D., et al., Prodigal: prokaryotic gene recognition and translation initiation site identification. 2010. 11(1): p. 119.|https://github.com/hyattpd/Prodigal/wiki/Introduction|
|`Python`|G. van Rossum, Python tutorial, Technical Report CS-R9526, Centrum voor Wiskunde en Informatica (CWI), Amsterdam, May 1995.|https://www.python.org/|
|`Qgrid`|NA|https://github.com/quantopian/qgrid|
|`SAMtools`|Li, H., et al., The sequence alignment/map format and SAMtools. 2009. 25(16): p. 2078-2079.|http://www.htslib.org/|
|`SPAdes`|Nurk, S., et al., metaSPAdes: a new versatile metagenomic assembler. Genome Res, 2017. 27(5): p. 824-834.|http://cab.spbu.ru/software/spades/|
|`Seqtk`|NA|https://github.com/lh3/seqtk|
|`Snakemake`|Köster, J. and S.J.B. Rahmann, Snakemake—a scalable bioinformatics workflow engine. 2012. 28(19): p. 2520-2522.|https://snakemake.readthedocs.io/en/stable/|
|`Tabix`|NA|www.htslib.org/doc/tabix.html|
|`tree`|NA|http://mama.indstate.edu/users/ice/tree/|
|`Trimmomatic`|Bolger, A.M., M. Lohse, and B. Usadel, Trimmomatic: a flexible trimmer for Illumina sequence data. Bioinformatics, 2014. 30(15): p. 2114-20.|www.usadellab.org/cms/?page=trimmomatic|
|`Virus-Host Database`|Mihara, T., Nishimura, Y., Shimizu, Y., Nishiyama, H., Yoshikawa, G., Uehara, H., ... & Ogata, H. (2016). Linking virus genomes with host taxonomy. Viruses, 8(3), 66.|http://www.genome.jp/virushostdb/note.html|
|`Virus typing-tools`|Kroneman, A., Vennema, H., Deforche, K., Avoort, H. V. D., Penaranda, S., Oberste, M. S., ... & Koopmans, M. (2011). An automated genotyping tool for enteroviruses and noroviruses. Journal of Clinical Virology, 51(2), 121-125.|https://www.ncbi.nlm.nih.gov/pubmed/21514213|

#### Authors:
- Dennis Schmitz ([RIVM](https://www.rivm.nl/en) and [EMC](https://www6.erasmusmc.nl/viroscience/))  
- Sam Nooij ([RIVM](https://www.rivm.nl/en) and [EMC](https://www6.erasmusmc.nl/viroscience/))  
- Robert Verhagen ([RIVM](https://www.rivm.nl/en))  
- Thierry Janssens ([RIVM](https://www.rivm.nl/en))  
- Jeroen Cremer ([RIVM](https://www.rivm.nl/en))  
- Florian Zwagemaker ([RIVM](https://www.rivm.nl/en))  
- Mark Kroon ([RIVM](https://www.rivm.nl/en))  
- Erwin van Wieringen ([RIVM](https://www.rivm.nl/en))  
- Harry Vennema ([RIVM](https://www.rivm.nl/en))  
- Annelies Kroneman ([RIVM](https://www.rivm.nl/en))  
- Marion Koopmans ([EMC](https://www6.erasmusmc.nl/viroscience/))  

____
_This project/research has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No. 643476._
____
