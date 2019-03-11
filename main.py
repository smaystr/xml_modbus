from servers.asyncserver import run_updating_server
from clients.signoflife import client_run
from multiprocessing import Process

if __name__ == "__main__":
    bdbs_p = Process(target=run_updating_server)
    sofl_p = Process(target=client_run)

    sofl_p.start()
    bdbs_p.start()

    sofl_p.join()
    bdbs_p.join()

