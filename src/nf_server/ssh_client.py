import os
import paramiko
from .key_storage import get_key
import logging
import time

def send_command(host, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {host}")
        try:
            client.connect(
                hostname = host, 
                username = os.getenv("SSH_USERNAME", "ubuntu"), 
                key_filename = get_key(host)
            )
        except Exception as e:
            logging.error(f"Failed to connect to {host}. {e}.")
            return {"status":-1, "message": "Error while connecting with host", "errors": e}

        logging.info(f"Connected to {host}")

        logging.info(f"Executing {command}")
        _, stdout, stderr = client.exec_command(command)

        while True:
            time.sleep(1)
            output = stdout.channel.recv(1024)
            if 'executor' in output.decode("utf-8"):
                # 'executor' means nextflow pipline started 
                # any further error will *hopefully* be reported by -with-weblog    
                logging.info("Job submitted successfully.")
                return {"status":0, "message": f"Job submitted successfully", "errors":[]}
            elif stdout.channel.exit_status_ready():
                # an exit status before pipeline started needs to be reported manually 
                exit_status = stdout.channel.recv_exit_status()
                error_message = stdout.readlines() + stderr.readlines()
                logging.error(f"Error while launching Nextflow. Exit Status: {exit_status}.  {error_message}.")
                return {"status":exit_status, "message":"Error while launching Nextflow", "errors": error_message}

    except Exception as e:
        logging.error(f"Error while sending command to host. {e}.")
        return {"status":-1, "message": "Error while launching Nextflow", "errors": e}

    finally:
        client.close()
