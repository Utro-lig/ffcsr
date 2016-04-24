# F-FCSR-H, Implementation and Attack

Here you can find a Python implementation of the F-FCSR-H stream cipher as well as
different implementations of a state recovery attack

## Getting Started

```
git clone https://github.com/ergrelet/ffcsr
cd ffcsr
```

### Prerequisities

- Python 3
- SageMath

### Using the F_FCSR_H class

See main.py to get an idea of how to use the F_FCSR_H class

### Generating the tables and dumps

Lookup tables are used in "attack_tables.py" and "attack_tables_mp.py" to make internal states' calculations' cost constant.  
To generate these table you'll need to edit "generate_tables.py" and set TABLES_PATH to the desired location.  
Then, typing the following instruction in sage:
```
attach("path_to_ffcsr_dir/generate_tables.py")
```
And to generate dumps, first edit "generate_dump.py", set the desired key and IV and set DUMP_PATH to the desired location  
Then, run:
```
python generate_dump.py
```

### Running the attack without lookup tables

To run the attack without lookup tables you'll need to edit "attack.py" and set DUMP_PATH to the location of your dump file  
Then, typing the following instruction in sage:
```
attach("path_to_ffcsr_dir/attack.py")
```

### Running the attack with lookup tables

To run the attack you'll need to edit "attack_tables.py" and set DUMP_PATH and TABLES_PATH to the locations of your dump and lookup tables  
And then simply run:
```
python attack_tables.py
```
or, if you want to use the multi-processing version of this attack:
```
python attack_tables_mp.py
```
