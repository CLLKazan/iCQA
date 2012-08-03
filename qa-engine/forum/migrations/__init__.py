import sys

class ProgressBar(object):
    def __init__(self, full):
        self.full = full
        self.count = 0

        self.print_bar(0)

    def print_bar(self, progress):
        sys.stdout.write("[%s%s] %d%%\r" % ('=' * progress, ' ' * (100 - progress), progress))
        sys.stdout.flush()

    def update(self):
        self.count += 1
        self.print_bar(int((float(self.count) / float(self.full)) * 100))