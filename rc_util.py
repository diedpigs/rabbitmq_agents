import logging
import argparse
from rc_rmq import RCRMQ
import json

rc_rmq = RCRMQ({'exchange': 'Register'})
confirm_rmq = RCRMQ({'exchange': 'Confirm'})
tasks = {'ohpc_account': False, 'ohpc_homedir': False, 'ood_account': False, 'slurm_account': False}
logger_fmt = '%(asctime)s [%(module)s] - %(message)s'

def add_account(username, full='', reason=''):
  rc_rmq.publish_msg({
    'routing_key': 'ohpc_account',
    'msg': {
      "username": username,
      "fullname": full,
      "reason": reason
    }
  })

def worker(ch, method, properties, body):
    msg = json.loads(body)
    task = msg['task']
    print("get msg: {}".format(task))
    tasks[task] = msg['success']

    # Check if all tasks are done
    done = True
    for key, status in tasks.items():
        if not status:
            print("{} is not done yet.".format(key))
            done = False 
    if done:
        confirm_rmq.stop_consume()
        confirm_rmq.delete_queue()
  
def consume(username, callback, debug=False):
    if debug:
        sleep(5)
    else:
        confirm_rmq.start_consume({
            'queue': username,
            'cb': callback
        })
  
    return { 'success' : True }

def get_args():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument('-n', '--dry-run', action='store_true', help='enable dry run mode')
    return parser.parse_args()

def get_logger(args=None):
    if args is None:
        args = get_args()

    logger_lvl = logging.WARNING

    if args.verbose:
        logger_lvl = logging.DEBUG

    if args.dry_run:
        logger_lvl = logging.INFO

    logging.basicConfig(format=logger_fmt, level=logger_lvl)
    return logging.getLogger(__name__)

