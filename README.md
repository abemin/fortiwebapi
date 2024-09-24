# fortiwebapi
Polling resources using fortiweb api and send to influxdb. Using grafana for dashboard.

# Steps
**1. Linux Server preferably Ubuntu**
   - set static IP
   - set NTP
   - `apt update && apt upgrade`  

**2. Install Docker**
   - `sudo apt install apt-transport-https curl`
   - `curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg`
   - `echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null`
   - `apt update`
   - `apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y`

**3. Install Influxdb & Grafana Docker**
   - use provided docker compose file.
   - take note of the influxdb details:
     - org: `my_api`  
     - bucket: `fwb_prod`    
     - token: `4KyZMUTc6VASAISdFhqtmhb8FXfDhhApBnh2wl81SEnULGvmUcmwvXKmxB8ZhGzu1PHHck3VDPH7g7Piv0mR8g==` **<-- your token**  
   - add influxdb datasource in grafana

**4. Install python3 on Linux Server with modules**
   - `apt install python3-full`
   - `apt install python3-requests`
   - `apt install python3-influxdb-client`

**5. Set hostname for influxdb and fortiweb.**
   - Google on how to create self-sign certificate.
   - Take note of the CA certificate.
   - Script is using "myCA.pem". Make sure this file is in the same directory as python script.
   - Set the host file "/etc/hosts". Make sure Linux server can resolve both hostname.

**6. Edit and test the script.**
   - edit the influxdb details.
   - edit the fortiweb api authorization token.
     - encode below to base64. can use terminal or online like www.base64encode.org.
     - `{"username":"your_username","password":"your_password","vdom":"root"}`
   - test the script.
   - `python3 fwb-to-influx.py`
   - expected result would be:  

global:  
global_cpu: 5  
global_memory: 53  
global_log_disk: 2  
global_tcp_concurrent_connection: 25  
global_tcp_connection_per_second: 0  
global_throughput_in: 0  
global_throughput_out: 0  
global_threat: 0  
name: web-server **<-- this is your policy name**  
web-server_tcp_concurrent_connection: 25  
web-server_tcp_connection_per_second: 0  
web-server_throughput_in: 0  
web-server_throughput_out: 0  
web-server_sessionCount: 25  
web-server_connCntPerSec: 0  
name: web-server-2 **<-- this is your policy 2 name**  
web-server-2_tcp_concurrent_connection: 0  
web-server-2_tcp_connection_per_second: 0  
web-server-2_throughput_in: 0  
web-server-2_throughput_out: 0  
web-server-2_sessionCount: 0  
web-server-2_connCntPerSec: 0  

**7. Set cronjob using crontab**
   - `crontab -e`
   - set below schedule to run every 10 second:  
\* * * * * python3 /home/administrator/pycsript/fwb_to_influx.py >> /dev/null  
\* * * * * sleep 10; python3 /home/administrator/pycsript/fwb_to_influx.py >> /dev/null  
\* * * * * sleep 20; python3 /home/administrator/pycsript/fwb_to_influx.py >> /dev/null  
\* * * * * sleep 30; python3 /home/administrator/pycsript/fwb_to_influx.py >> /dev/null  
\* * * * * sleep 40; python3 /home/administrator/pycsript/fwb_to_influx.py >> /dev/null  
\* * * * * sleep 50; python3 /home/administrator/pycsript/fwb_to_influx.py >> /dev/null  

**8. Add 1.json dashboard to grafana. Edit the query as per your setting.**

