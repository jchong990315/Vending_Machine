# Research Report
## Actual MySQL connection implementation research

### Summary of Work
This research aims to find out the most appropriate way to make our MySQL database connected to our Django. It involves several usages of external libraries.

### Motivation
Due to the complexity of our program, we need to achieve a most efficient way to implement database connection. It can ensure our transactions and communications can be precisely updated in our database.

### Time Spent
- **Understanding basic structure of connection logic (30 minutes)**: Viewing official Django documentation on MySQL connection tutorial
- **Research on what external libraries are useful (30 minutes)**: Figure our how to adapt the tutorial to our db which is running on docker on VM.( SSH tunneling foward wrapper, etc)

### Results
For DB configuration in setting.py, the Django research report has already covered such information. Other than that, I have refined the configuration to fit our db:
``` python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Vending_Machine',
        'USER': 'root',
        'PASSWORD': 'Group17',
        # Use the VM's IP address or the docker service name if on the same network.
        'HOST': 'your_vm_ip_or_hostname',  
        'PORT': '53386',
    }
}
```
After running python setting.py migrate; we will see if it connects.
If not, we need to add a forward.py for automatic ssh tunnel while runnning our app
##### Campus VPN will be required here

``` python
from sshtunnel import SSHTunnelForwarder
import MySQLdb

with SSHTunnelForwarder(
      ('ssh_host', 22),
      ssh_password="ssh_password",
      ssh_username="ssh_username",
      remote_bind_address=('mysql_host', 3306)) as server:

     con = MySQLdb.connect(user='mysql_username',passwd='mysql_password',db='mysql_db_name',host='mysql_host',port=server.local_bind_port)
```

#### Implementation Steps for Connection:
1. Go to VM to take notes of the server ip
2. update configurations in setting.py with the noted ip and the db construct file
3. (May need for bypass VM authentication) Construct a forward.py for SSH tunnel 
4. Finish up corresponding query requests
