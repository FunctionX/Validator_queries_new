import requests
import subprocess
from subprocess import Popen,PIPE, TimeoutExpired, CalledProcessError
import json
from utils import exception_logger
import logging

# validator_info = ["fxcored","q","staking","validators","--node=https://fx-json.functionx.io:26657"],
# "create_val":["fxcored","q","txs","--events","message.action=create_validator","--node=https://fx-json.functionx.io:26657","--limit=100"],
# "val_withdrawals":["fxcored","q","txs","--events","msg","--node=https://fx-json.functionx.io:26657"],
# "val_outstanding_comms":["fxcored","q","distribution","commission","val","--node=https://fx-json.functionx.io:26657"],
# "delegator_rewards":["fxcored","q","distribution","rewards","wallet","--node=https://fx-json.functionx.io:26657"]

def get_val_outstanding_rewards(validator_address):
    r = requests.get(f'https://fx-rest.functionx.io/cosmos/distribution/v1beta1/validators/{validator_address}/outstanding_rewards')
    print(r.text)

def get_val_commission(validator_address):
    r = requests.get(f'https://fx-rest.functionx.io/cosmos/distribution/v1beta1/validators/{validator_address}/commission')
    print(r.text)

def get_staking_validators():
    r = requests.get('https://fx-rest.functionx.io/cosmos/staking/v1beta1/validators')
    return r.text


# ======================================================fxcore commands======================================================

def get_validator_address_cmd(validator_address:str)->list:
    validator_keys = ["fxcored","keys","parse","fxvaloper1lgzkn292ap2a4t8dvsq0cf5qfkkuplcnztcnvp"]
    validator_keys[3] = validator_address
    return validator_keys



def get_val_outstanding_comms_cmd(validator_address:str):
    """
    get outstanding comms for validator
    """
    val_outstanding_comms = ["fxcored","q","distribution","commission","val","--node=https://fx-json.functionx.io:26657"]
    val_outstanding_comms[4]=validator_address
    return val_outstanding_comms


def get_val_outstanding_delegated_rewards_cmd(validator_wallet_address:str):
    delegator_rewards = ["fxcored","q","distribution","rewards","wallet","--node=https://fx-json.functionx.io:26657"]
    delegator_rewards[4] = validator_wallet_address
    return delegator_rewards

def _create_msg_string(validator_address:str)->str:
    """
    takes in validator address and msg action string
    """
    msg_string=f"message.sender={validator_address}&message.module=distribution"
    return msg_string

def get_all_withdrawals_cmd(validator_address):
    msg = _create_msg_string(validator_address)
    cmd = ["fxcored", "query", "txs", "--events", msg, "--node=https://fx-json.functionx.io:26657"]
    return cmd



# @exception_logger
# def _get_raw_data(cmd:list)->dict:
#     """
#     CLI command to return raw_data output
#     """
#     data=subprocess.run(cmd,stdout=subprocess.PIPE)
#     # change byte to string
#     data_decode=data.stdout.decode('utf-8')
#     print(data_decode)
#     dict_data=json.loads(data_decode)
#     return dict_data

# ---------------check type of cmd if based on the 1st and 2nd input--------------
def determine_cmd_type(cmd:list)->str:
    """
    check to see the type of tx
    """
    cmd_type = f"{cmd[1]}-{cmd[2]}"
    return cmd_type


# --------------------------run cmd---------------------------
@exception_logger
def run(cmd):
    """
    run CLI command and log info
    """
    cmd_type = determine_cmd_type(cmd)
    try:
        p1=subprocess.run(cmd,capture_output=True,text=True, timeout=45)
        args=" ".join(p1.args)
        if (p1.returncode==0):
            # stdout=p1.stdout.split('\n', 1)[0]
            stdout = json.loads(p1.stdout)
            logging.info("%s,%s,%s"%(cmd_type,args,stdout))
            return stdout
        else:
            stderr=p1.stderr.split('\n', 1)[0]
            logging.error("%s,%s,%s"%(cmd_type,args,stderr))
            return stderr
    except TimeoutExpired:
        logging.error("Timeout happened.\n")

# fxcored query distribution rewards fx1a73plz6w7fc8ydlwxddanc7a239kk45jmwcesj
# fxcored query distribution commission fxvaloper1a73plz6w7fc8ydlwxddanc7a239kk45jnl9xwj
# fxcored query txs --events 'message.sender=fxvaloper19psvqem8jafc5ydg4cnh0t2m04ngw9gfqkeceu&message.module=distribution'

