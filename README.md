# pyVSimPipe
 VSimPipe  Simple command line tools for running simulations using qsub.

  Be minded you need to have singularity installed to use singularity mode
  (default).

  To start a new set of simulations first do:

  ``` > VSimPipe init```

  This will generate a set of default configuration files and a order file
  (order.csv).

  Next, edit the necessary fields in the config file and order file.

  Now, you are ready to send the simulations out:

  ```> VSimPipe run```

Options:  
  --log-level [DEBUG|INFO|WARNING|ERROR]  
                                  Logging verbosity level  
  --show-warnings TEXT            Show warnings?  
  --help                          Show this message and exit.  

Commands:  
  init  
  run  
  
 # Install
 
 Just run:
 
 ``` > pip install . ``` 
 
