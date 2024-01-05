# NOTE for thor_reproduce
This is for extracting isabelle data from afp.
Setup according the installation steps below.

TODO: Rebase my commits on top of main branch onto isabelle2021 branch & merge with thor-client-isabelle2021 branch

# PISA (Portal to ISAbelle)
PISA supports automated proof search with the interactive theorem prover [Isabelle](https://isabelle.in.tum.de).

PISA can also be used to extract proof corpus. We extracted the datasets in our AITP 2021 paper [LISA: Language models of ISAbelle proofs](http://aitp-conference.org/2021/abstract/paper_17.pdf) with it.


## Installation
1. **Scala configuration**
   
    Install SDKMAN
    ```shell
    curl -s "https://get.sdkman.io" | bash
    source .bashrc
    ```
    Try
    ```shell
    sdk help
    ```
    to makes ure sdk is properly installed.
    
    Install JAVA 11 and sbt
    ```shell
    sdk install java 11.0.11-open
    sdk install sbt
    ```
2. **Clone project and make sure it compiles**

    ```shell
    git clone https://github.com/albertqjiang/Portal-to-ISAbelle.git
    cd Portal-to-ISAbelle
    ```

    Then compile the project:
    ```shell
    sbt compile
    ```
   
3. **Configure Isabelle**

    Go back to home directory first and download isabelle2021
    ```shell
    cd ~
    wget https://isabelle.in.tum.de/website-Isabelle2021/dist/Isabelle2021_linux.tar.gz
    tar -xzf Isabelle2021_linux.tar.gz
    alias isabelle=~/Isabelle2021/bin/isabelle
    ``` 
    
4. **Build Isabelle HOL**
   
   To build with 20 parallel processes:
   ```shell
   isabelle build -b -D Isabelle2021/src/HOL/ -j 20
   ```
   This takes ~8 hours of CPU time. The actual time depends on the number of CPUs you have. On a 96-core TPU VM it takes about 15 minutes.

5. **Download and build afp**
   #### Option A. Build manually (recommended)

   To build with 10 parallel processes:
   ```shell
   hg clone ssh://hg@foss.heptapod.net/isa-afp/afp-devel -r 002a907668c5877a8c1aded2427c5364ff16adfb # ssh-keygen and add ssh key to your gitlab account first
   mv afp-devel afp-2021-02-11
   export AFP=afp-2021-02-11/thys
   isabelle build -b -D $AFP -j 20
   ```

   #### ~~Option B. Use built-in heap images~~
   There is built-in heap images, but not for afp-2021-02-11.

   **I chose to use afp-2021-02-11 instead of afp-2021-10-22, as afp-2021-10-22 is mostly incompilable with Isabelle2021 due to "document_logo" options in the ROOT files (which seemed to be added after Isabelle2021)**.

   We built the heap images for two options.
   1. Isabelle2021 with afp-2021-10-22 for linux machines (ubuntu). You can download it at:
   https://archive.org/download/isabelle_heaps.tar/isabelle_heaps.tar.gz
   and decompress it as ~/.isabelle.
   2. Isabelle2022 with afp-2022-12-06 for linux machines (ubuntu). You can download it at:
   https://archive.org/download/isabelle2022_afp20221206_heaps/isabelle2022heaps.tar.gz and decompress it as ~/.isabelle.

   Note: this does not always work on different operating systems.

## Extract PISA dataset (for fine-tuning)
   ### 1. Get extracted archive of formal proofs
   
   #### Option A. Use pre-extracted dataset (recommended)
   Available for download at https://archive.org/download/afp_extractions.tar/afp_extractions.tar.gz.

   #### ~~Option B. Extract manually (not tested)~~

   Generate commands for extracting proofs.
   Edit line 9 of command_generation/generate_commands_afp.py so that it uses your actually home directory.
   Run the following command:
   ```shell
   python command_generation/generate_commands_afp.py
   ```
   and follow the instructions. At the first step it asks you which ports you want to use. We current support ports 8000-8200, 9000, 10000, 11000, 12000. You can also add your favourites by editing src/scala/server/PisaOneStageServers.scala. This dictates how many processes for extraction you wish to run at the same time.

   It should say "A total of X files are due to be generated" with X > 5000.
   And you should see files called afp_extract_script_${port_number}.sh in the directory.

   To extract the files, run the following commands to install necessary libraries and execute the commands:
   ```shell
   pip install grpc
   pip install func_timeout
   bash afp_extract_script_${port_number_1}.sh &
   bash afp_extract_script_${port_number_2}.sh &
   bash afp_extract_script_${port_number_3}.sh &
   ...
   bash afp_extract_script_${port_number_n}.sh &
   ```

   With a single process, the extraction takes ~5 days. This will extract files to the directory afp_extractions. 
   
   ### 2. Extract training, validation, test data
   Prepare data format for [thor_reproduce/data.custom_loader.py](https://github.com/AnHaechan/thor_reproduce/blob/main/data/custom_loader.py) by the following command.
   ```
   python3 src/main/python/legacy/prepare_episodic_transitions.py -efd <path_to_afp_extractions> -sd <directory_to_save> --last-1
   ```

   Examples at `extracted_data_small_episodic_last_k`.

   Then upload the data into gcloud bucket, and setup the path accordingly in thor-reproduce.
   
   <!-- To extract state-only source-to-target pairs, run the following command:
   ```shell
   python3 src/main/python/prepare_episodic_transitions.py -efd afp_extractions -sd data/state_only --state
   ```

   To extract proof-only source-to-target pairs, run the following command:
   ```shell
   python3 src/main/python/prepare_episodic_transitions.py -efd afp_extractions -sd data/proof_only --proof
   ```

   To extract proof-and-state source-to-target pairs, run the following command:
   ```shell
   python3 src/main/python/prepare_episodic_transitions.py -efd afp_extractions -sd data/proof_and_state --proof --state
   ```
   Note that extraction involving proofs will take pretty long and will result in large files. State-only files amount to 8.1G. With proof steps it's even much larger. -->

# Acknowledgement
This library is heavily based on [scala-isabelle](https://github.com/dominique-unruh/scala-isabelle), the work of Dominique Unruh. We are very grateful to Dominique for his kind help and guidance.

# Citation
If you use this directory, or our code, please cite the paper we published at AITP 2021.
```bibtex
@article{jiang2021lisa,
  title={LISA: Language models of ISAbelle proofs},
  author={Jiang, Albert Q. and Li, Wenda and Han, Jesse Michael and Wu, Yuhuai},
  year={2021},
  journal={6th Conference on Artificial Intelligence and Theorem Proving},
}
```

<!-- # Untested legacy stuff
**The following content was built on the 2020 version of Isabelle with afp-2021-02-11. They have not been tested with Isabelle2021 and might contain bugs.**
## Running proof search
After the heap images have been built, experiments of proof searching can be run.
1. Configure the Isabelle binary path and the AFP path
   
   Go to PisaSearch.scala, change the second string of line 352 so that it points to your afp path.
   
   Change the string in line 383 so that it points to the directory where Isabelle was installed.
   
   (For the last two steps, be careful because the substitution is based on strings and quite subtle. Make sure everything checks out.)
   
   Lines 46-79 contain the querying commands. Change these to use OpenAI's internal API.

2. Get the universal test theorem names

   ```shell
   cd Portal-to-ISAbelle
   wget http://www.cs.toronto.edu/~ajiang/universal_test_theorems.tar.gz
   tar -xzvf universal_test_theorems.tar.gz
   ```
3. Generate the proof search scripts
   
   ```shell
   mkdir results
   python command_generation/search_command_generator.py
   ```
   Follow the instructions.

4. Run the proof search experiments
   
   In scripts, some files have been generated in the format of 
   eval_search_conj_{boolean}_use_proof_{boolean}_use_state_first_{boolean}_{$script_number}.sh
   
   Wrap them with Python to use subprocesses.

   The results will be in the results directory.


### Python packages
grpc

It might work with lower versions but they have not been tested.

## Usage
<!-- ### Build AFP heap images
First you should know the path to the Isabelle binary executable. 
On MacOS, with Isabelle2020, the path to it is
```shell
/Applications/Isabelle2020.app/Isabelle/bin/isabelle
```
On linux, it might be
```shell
~/Isabelle2020/bin/isabelle
```

I will alias this to isabelle for convenience:
```shell
alias isabelle="PATH TO THE EXECUTABLE"
```

Download the [Archive of Formal Proofs](https://www.isa-afp.org/download.html).
We use the version afp-2021-02-11 for data extraction, but a later version is also fine.
Let's say the path to this is AFP_PATH. Build the afp entries:
```shell
isabelle build -b -D $AFP_PATH/thys
```
This will take ~12 hours with an 8-core CPU. 
You should check that in the process, heaps are built for each afp project in the directory
```shell
~/.isabelle/Isabelle2020/heaps/polyml-5.8.1_x86_64_32-darwin
```
(The exact path might differ if you have different OS or polyml verions but should be easy to find) -->


<!-- ### Model evaluation
See src/main/python/load_problem_by_file_and_name.py for an example of using an oracle theorem prover 
to evaluate on some problems. 

Notice in line 101, the theory file path is altered. 
This is because the afp extraction and evaluation happened on different machines.
Comment this line out if you manually extracted the afp files, or swap 
```shell
/Users/qj213/Projects/afp-2021-02-11
```
for the location of afp files on your computer.

When doing evaluation, in one terminal, run
```shell
sbt "runMain pisa.server.PisaOneStageServer9000"
```
You can switch to port 8000, 10000, 11000, or 12000. 9000 is the default used in the Python file.
In another terminal, use Python function evaluate_problem to obtain a proof success or failure.

You will need to pass in a model as an argument that has the method predict. 
model.predict takes in a string of proof state, and return the next proof transition.

The evaluate_problem method executes prediction for a maximum of 100 steps by default.

Problem evaluation currently only allows agents based on proof states only.
Agents based on previous proof segments and hybrid-input agents will be supported in the near future. -->
