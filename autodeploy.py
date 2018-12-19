
import sys, os
import time
import traceback
import subprocess, signal
import git
import datetime

APP_NAME = 'autodeploy'

def git_pull():
    global APP_NAME
    # returns true if there are changes
    repo = git.Git()
    old_hash = repo.log().split('\n')[0]
    g = git.cmd.Git()
    g.pull()
    new_hash = repo.log().split('\n')[0]
    has_pulled_something = new_hash != old_hash
    if has_pulled_something:
        log_msg = repo.log().split('\n')[4]
        print str(datetime.datetime.now()), '['+str(APP_NAME)+']', 'Upgrades...', log_msg
    return has_pulled_something

def is_alive(pid):
    # returns true if there is a process with such a pid
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def term(pid):
    global APP_NAME
    print str(datetime.datetime.now()), '['+str(APP_NAME)+']', 'term', pid
    os.kill(pid, signal.SIGTERM)
    for i in range(50):
        time.sleep(0.1)
        if not is_alive(pid):
            return
    print str(datetime.datetime.now()), '['+str(APP_NAME)+']', 'kill', pid
    os.kill(pid, signal.SIGKILL)

def start_program(program_and_args):
    global APP_NAME
    print str(datetime.datetime.now()), '['+str(APP_NAME)+']', 'run', program_and_args
    pid = subprocess.Popen(program_and_args, shell=False).pid
    print str(datetime.datetime.now()), '['+str(APP_NAME)+']', 'running with pid:', pid
    return pid

def main():
    global APP_NAME
    if len(sys.argv) <= 2:
        print 'Usage:'
        print '\tpython autodeploy.py <path> <program> [args...]'
        return
    path = sys.argv[1]
    program_and_args = sys.argv[2:]
    print str(datetime.datetime.now()), '['+str(APP_NAME)+']', 'entering path', path
    print str(datetime.datetime.now()), '['+str(APP_NAME)+']', 'running with', program_and_args
    os.chdir(path)
    git_pull()
    pid = None  
    try:
        while True:
            try:
                pid = start_program(program_and_args)
                while True:
                    try:
                        time.sleep(10)
                        if not is_alive(pid):
                            break
                        if git_pull():
                            term(pid)
                            break
                    except KeyboardInterrupt, e:
                        raise e
                    except Exception, e:
                        print str(datetime.datetime.now()), '['+str(APP_NAME)+']', e
                        print str(datetime.datetime.now()), '['+str(APP_NAME)+']', traceback.format_exc()
            except KeyboardInterrupt, e:
                raise e
            except Exception, e:
                print str(datetime.datetime.now()), '['+str(APP_NAME)+']', e
                print str(datetime.datetime.now()), '['+str(APP_NAME)+']', traceback.format_exc()
                time.sleep(1)
    except KeyboardInterrupt:
        term(pid)


if __name__ == "__main__":
    main()
