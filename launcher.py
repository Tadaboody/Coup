from Coup import Coup
import player
from ast import literal_eval



class ProgressBar:
    def __init__(self, total):
        self.index = float(0)
        self.total = float(total)
        self.progress = float(self.index / total) * 100

    def update(self):
        self.index += 1
        a = float((self.index / self.total))
        a *= 100
        if int(a) != int(self.progress):
            self.progress = (self.index / self.total) * 100
            print str(int(self.progress)) + '%'


winners = [0] * 4
total = input("Amount of runs?")

prog = ProgressBar(total)
crashing_seeds = list()
seed = None
if input("seed to crash?"):
    with open("seeds.txt") as seed_file:
        crashing_seeds = seed_file.readlines()
        seed = crashing_seeds[0]
        seed = literal_eval(seed)
for i in xrange(total):
    game = Coup(players=(player.RandomAI(), player.RandomAI(), player.RandomAI(),player.ThinkingAI()),seed=seed,should_print=False)
    try:
        game.run_game()
    except RuntimeError as r:
        print r.message
        crashing_seeds.append(game.seed)
        continue
    winners[game.winner.num - 1] += 1
    prog.update()
with open("seeds.txt", 'wb') as file:
    for seed in crashing_seeds:
        print >> file, seed
print winners
winnersum = 0
for player in winners:
    winnersum += player
if winnersum:
    print str(float(winners[-1]) / float(winnersum) * 100) + '%'
