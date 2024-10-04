# ITeratOr


## How to run

1. Run setup.sh to install the required packages on Linux.

    ```
    sudo chmod +x setup.sh
    ./setup.sh
    ```

2. Start app

    ```
    python3 ./main.py (-p | -e)
    
    -p  Use physical watch
    -e  Use emulated watch

## When developing
- separate everything into folders and functions to make development easier
- use the logger.info or logger command to note each critical setp or command used during script execution
    - https://docs.python.org/3/howto/logging.html