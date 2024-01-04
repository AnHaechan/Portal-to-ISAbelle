# NOTE for thor_reproduce
This is for isabelle2021 server for pisa client.
Replace `pisa_path` in the [thor_reproduce/solvers.bfs_solvers.start_isabelle](https://github.com/AnHaechan/thor_reproduce/blob/main/solvers/bfs_solvers.py#L559C26-L559C26) with the path to this repository.
Configure isabelle beforeahand by following instructions in the [thor_reproduce](https://github.com/AnHaechan/thor_reproduce).
Only "scala side" (src/main/scala/pisa) will be used of this branch.

Additionally, testing sledgehammer-only on the benchmark is done in this repository.
```
python3 command_generation/hammer_command_generator.py
// For now, use run 3 processes at the same time (in the paper it is mentioned that an Isabelle process has access up to 32 CPU and we have 96 cores in the TPU VM)
// Don't use heuristics to run hammer-only

chmod +x scripts/eval_hammer_*.sh

./scripts/eval_hammer_0.sh > script0.log 2>&1 &
./scripts/eval_hammer_1.sh > script1.log 2>&1 &
./scripts/eval_hammer_2.sh > script2.log 2>&1 &
wait

python3 gather_hammer_results.py // to read results in `results/hammer_eval/`
```

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
    Go into the file build.sbt and change the $PWD on line 19 with the actual path of the current working directory, such that we have the absolute path of the scala-isabelle jar file. For example, the line should look like:
    libraryDependencies += "de.unruh" %% "scala-isabelle" % "master-SNAPSHOT" from "file:/home/aqj/Portal-to-ISAbelle/lib/scala-isabelle_2.13.jar".

    Then compile the project:
    ```shell
    sbt compile
    ```

## Evaluation setup (if you want to have N (N>50) PISA servers running on your machine)
1. **Create some PISA jars**

   For a single process, sbt is good enough. But for multiple processes, to have native JAVA processes running is a better idea. We first use sbt-assembly to create a fat jar (a jar where all the java code is compiled into and can be run independently).
   ```shell
   sbt assembly
   ```

   The assembly process should take less than 5 minutes. The compiled jar file is in the target/scala-2.13/ directory as PISA-assembly-0.1.jar. You can then copy the PISA jar for N times if you want the jars to be truly independent and separated by calling the following script:
   ```shell
   python eval_setup/copy_pisa_jars.py --pisa-jar-path target/scala-2.13/PISA-assembly-0.1.jar --number-of-jars $N --output-path $OUTPUT_PATH
   ```

2. **Create some Isabelle copies**

   This step is to create multiple copies of the Isabelle software as well as the built heap images to avoid IO errors which can occur when many processes are run at the same time. We use $ISABELLE to denote where your Isabelle software lives and $ISABELLE_USER to denote where your built heap images live, which is usually at $USER/.isabelle

   Note that one copy of the Isabelle software plus all the heaps needed for the Archive of Formal Proofs amount to **35GB** of disk space. So create copies with care. Alternatively, you can start by trimming the heaps so only the ones you need are kept.

   Use the following script to create the copies:
   ```shell
   python eval_setup/copy_isabelle.py --isabelle $ISABELLE --isabelle-user $ISABELLE_USER --number-of-copies $N --output-path $OUTPUT_PATH
   ```

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
