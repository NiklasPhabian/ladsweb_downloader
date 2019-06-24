import datetime

class ETA():
    def __init__(self, n_tot):
        self.start = datetime.datetime.now()
        self.n = 0
        self.n_tot = n_tot
        print('total number: {}'.format(n_tot))

    def eta(self):
        total_eleapsed = datetime.datetime.now() - self.start
        avg_duration = total_eleapsed.total_seconds()/self.n
        n_left = self.n_tot - self.n
        seconds_left = int(avg_duration * n_left)
        eta = datetime.timedelta(seconds=seconds_left)
        return eta

    def display(self, step=None):
        self.n += 1       
        now = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        if step is not None:
            message = '{now} {step} - ETA in {eta}'.format(now=now, step=step, eta=self.eta())
        else:
            message = '{now} ETA in {eta}'.format(now=now, eta=self.eta())
        print(message)
 
