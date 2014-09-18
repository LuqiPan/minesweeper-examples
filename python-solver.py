import httplib, urllib, random, copy, random

HOST = "minesweeper.nm.io"

class PythonSolver:
  def __init__(self, game_name):
    if game_name is None:
      raise Exception("A game name is required")
    self.game_name = game_name
    self.board_size = {}
    self.board = None
    self.board_mine_count = None

  def parse_board(self, board):
    board_string = board.split(",")
    if len(board_string) != 3:
      raise Exception("Error in input: %s", board)
    x = int(board_string[0])
    y = int(board_string[1])
    self.board_size["x"] = x
    self.board_size["y"] = y
    self.board_mine_count = board_string[2]
    self.board = [[None for a in xrange(x)] for a in xrange(y)]

  def print_board(self):
    """Prints the board to STDOUT"""
    if self.board is None:
      raise Exception("Please start a new game")

    for i in xrange(self.board_size["x"]):
      for j in xrange(self.board_size["y"]):
        if self.board[j][i] is None:
          print "?",
        else:
          print self.board[j][i],
      print

  def in_bounds(self,x,y):
    """Helper method to decide if coord is inside of the board"""
    if (x < 0 or y < 0):
      return False
    if (x >  self.board_size['x'] - 1 or y > self.board_size['y'] - 1):
      return False
    return True

  def neighbor_coords(self,x,y):
    """Returns the coordinates of the neighbourhood, taking into account board dimensions"""
    neighbors = []
    if self.in_bounds(x+1, y+1): neighbors.append([x+1,y+1])
    if self.in_bounds(x+1, y): neighbors.append([x+1,y])
    if self.in_bounds(x-1, y-1): neighbors.append([x-1,y-1])
    if self.in_bounds(x-1, y): neighbors.append([x-1,y])
    if self.in_bounds(x-1, y+1): neighbors.append([x-1,y+1])
    if self.in_bounds(x, y+1): neighbors.append([x,y+1])
    if self.in_bounds(x+1, y-1): neighbors.append([x+1,y-1])
    if self.in_bounds(x, y-1): neighbors.append([x,y-1])
    return neighbors

  def info(self):
    """Calls the info endpoint to get the board size"""
    conn = httplib.HTTPConnection(HOST)
    conn.request("GET", "/info")
    data = conn.getresponse().read()
    conn.close()
    return data

  def guess(self, x, y):
    params = urllib.urlencode({"id": self.game_id, "x": x, "y": y})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(HOST)
    conn.request("POST", "/open", params, headers)
    response = conn.getresponse()
    conn.close()
    return response.read()

  def new_game(self):
    # If there is no current game, bail
    if self.game_name is None:
      raise Exception("No game name set")
    # Call the API { POST /new } to get a new game
    params = urllib.urlencode({'name': self.game_name})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(HOST)
    conn.request("POST", "/new", params, headers)
    response = conn.getresponse()
    self.game_id = response.read()
    conn.close()
    # Reset the board
    self.parse_board(self.info())

  def random_solve(self):
    """ Example solver that tries to solve a minesweeper game by bruteforcing random positions"""
    while True:
      # Choose a position at random within the bounds of the board
      x = random.randint(0, self.board_size["x"]-1)
      y = random.randint(0, self.board_size["y"]-1)
      guess_result = None

      # If this position hasn't been opened before
      if self.board[x][y] is None:
        # Calls guess, returning an int with the number of mines, win or lost
        guess_result = self.guess(x,y)
        print " Random Guess: (%s,%s): %s" % (x, y, guess_result)
        # If we won or lost, bail
        if guess_result == "win":
          return "win"
        if guess_result == "lost":
          return "lost"
        # Fill the result on the board
        self.board[x][y] = guess_result
        self.print_board()

  def my_solver(self):
    """Fill in this solver with your logic"""
    q = []
    while True:
      fi = False
      while len(q) > 0:
        r = q.pop(0)
        x = r[0]
        y = r[1]
        # print(q)
        if self.board[x][y] is None:
          fi = True
          break
      if not fi:
        prob_board = copy.deepcopy(self.board)
        for i in range(len(prob_board)):
          for j in range(len(prob_board[0])):
            prob_board[i][j] = 0#999999
        
        for i in range(len(prob_board)):
          for j in range(len(prob_board[0])):
            if self.board[i][j]:
              cur = int(self.board[i][j])
              for a in range(-1, 2):
                for b in range(-1, 2):
                  nx = i + a
                  ny = j + b
                  if (nx >= 0) and (nx < self.board_size['x']) \
                      and (ny >= 0) and (ny < self.board_size['y']):
                    if (nx != i) or (ny != j):
                      # if prob_board[nx][ny] >= 999999:
                        # prob_board[nx][ny] = 0
                      prob_board[nx][ny] += cur
        
        min_score = 999999
        min_pos = []
        for i in range(len(prob_board)):
          for j in range(len(prob_board[0])):
            if self.board[i][j] is None:
              #if self.board[i+1][j] != None or self.board[i-1][j] != None or self.board[i][j+1] != None or self.board[i][j-1] != None or self.board[i-1][j-1] != None or self.board[i-1][j+1] != None or self.board[i+1][j-1] != None or self.board[i+1][j-1] != None:
                if prob_board[i][j] < min_score:
                  min_score = prob_board[i][j]
                  min_pos = []
                if prob_board[i][j] == min_score:
                  min_pos.append((i, j))
          
        pos = random.sample(min_pos, 1)[0]
        x = pos[0]
        y = pos[1]
      guess_result = self.guess(x, y)
      # print " Random Guess: (%s,%s): %s" % (x, y, guess_result)
      # If we won or lost, bail
      if guess_result == "win":
        print(guess_result)
        return "win"
      if guess_result == "lost":
        print(guess_result)
        return "lost"
      if int(guess_result) == 0:
        for a in range(-1, 2):
          for b in range(-1, 2):
            nx = x + a
            ny = y + b
            if (nx >= 0) and (nx < self.board_size['x']) \
                and (ny >= 0) and (ny < self.board_size['y']):
              if (nx != x) or (ny != y):
                q.append((nx, ny))
      # Fill the result on the board
      self.board[x][y] = guess_result
      # self.print_board()

if __name__ == "__main__":

  # CHANGE HERE ------------------------------
  solver = PythonSolver("caonima57@brown.edu") # XXX: Replace this with your own unique name
  solver_alg = solver.my_solver      # XXX: Replace this with your own solver method
  GAMES = 100                           # XXX: replace this with the number of games that you want to play
  # -------------------------------------------

  results = []
  for _ in range(GAMES):
    print "# Starting new Game"
    solver.new_game()
    results.append(solver_alg())
    # print " Final board:"
    # print
    # solver.print_board()
    # print
  print "Final Results: %s Wins, %s Losses" % (results.count("win"), results.count("lost"))
