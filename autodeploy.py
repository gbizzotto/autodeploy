
import sys, os
import time
import traceback
import subprocess, signal
import git
import datetime

def git_pull():
    # returns true if there are changes
    print str(datetime.datetime.now()), 'git_pull'
    repo = git.Git()
    old_hash = repo.log().split('\n')[0]
    g = git.cmd.Git()
    g.pull()
    new_hash = repo.log().split('\n')[0]
    has_pulled_something = new_hash != old_hash
    print str(datetime.datetime.now()), 'has pulled something:', has_pulled_something
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
    print str(datetime.datetime.now()), 'term', pid
    os.kill(pid, signal.SIGTERM)
    for i in range(50):
        time.sleep(0.1)
        if not is_alive(pid):
            return
    print str(datetime.datetime.now()), 'kill', pid
    os.kill(pid, signal.SIGKILL)

def start_program(program_and_args):
    print str(datetime.datetime.now()), 'run', program_and_args
    pid = subprocess.Popen(program_and_args, shell=False).pid
    print str(datetime.datetime.now()), 'running with pid:', pid
    return pid

def main():
    if len(sys.argv) <= 2:
        print 'Usage:'
        print '\tpython autodeploy.py <path> <program> [args...]'
        return
    path = sys.argv[1]
    program_and_args = sys.argv[2:]
    print str(datetime.datetime.now()), 'entering path', path
    print str(datetime.datetime.now()), 'running with', program_and_args
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
                    except Exception, e:
                        print str(datetime.datetime.now()), e
                        print str(datetime.datetime.now()), traceback.format_exc()
            except Exception, e:
                print str(datetime.datetime.now()), e
                print str(datetime.datetime.now()), traceback.format_exc()
                time.sleep(1)
    except KeyboardInterrupt:
        term(pid)


if __name__ == "__main__":
    main()