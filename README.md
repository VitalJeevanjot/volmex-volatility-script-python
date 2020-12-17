For automatic basic monitoring:

Monit (Using): First setup `monitrc` file to use pid `/var/run/evix.pid` and to start and stop do `start = "<path-to-evix> start"` & `stop = "<path-to-evix> stop"`

Run the process first to get it's pid with ...
    - evix (script): to start this script and create it's process id for monit (Set it's path in script to INDEX.py) (also change it's permission to make it executable)
    **Then start monit**
    *Note*: If starting from bash, then make sure to include full path of INDEX.py from root directory.
    > Use *absolute path* in all scripts and change according in INDEX.py where ever `firebase admin config` or `.env` files are requested
    > Make sure to output logs from evix script, Example
    ```
    check process volmex-script-process with pidfile /var/run/evix.pid
       start = "/bin/bash -c '/root/monit/volmex/evix start &>/tmp/evix-script-logs-start.out'"
       stop = "/bin/bash -c '/root/monit/volmex/evix stop &>/tmp/evix-script-logs-stop.out'"
    ```

supervisor(not maintained):
    - Dockerfile : creates image with supervisor running our script
    - volmex.conf : configs for supervisor 

plain(not maintained):
    - script.sh : consist several methods to do auto resart on script crash