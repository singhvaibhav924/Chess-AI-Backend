import numpy as np
import chess
import tflite_runtime.interpreter as tflite

class Model_handler :
  def __init__(self) :
    self.interpreter = tflite.Interpreter(model_path="model.tflite")
    self.interpreter.allocate_tensors()
    print("Model loaded and is ready to use !!!")

  def predict(self, state, color) :
    input_data = self.convert_state_to_input(state, color)
    input_details = self.interpreter.get_input_details()
    output_details = self.interpreter.get_output_details()
    print(input_details)
    print(output_details)
    self.interpreter.set_tensor(input_details[0]['index'], input_data[0])
    #self.interpreter.set_tensor(input_details[1]['index'], input_data[1])
    
    self.interpreter.invoke()
    
    output_data = self.interpreter.get_tensor(output_details[0]['index'])
        
    return self.convert_output_to_probs(state, color, output_data[0])

  def convert_state_to_input(self, state, color) :
    if type(state) == str :
      temp = state.split("_")
      temp_arr = np.zeros((8,8,12), dtype = np.float32)
      arr2 = np.zeros((8,8,10), dtype = np.float32)
      temp_arr, arr2 = self.convert_board_to_input(temp[-1], color)
      for i in range(1,5) :
        temp_arr = np.concatenate([self.convert_board_to_input(temp[-1-i], color, False), temp_arr], axis = 2)
      return (np.expand_dims(temp_arr, axis = 0), np.expand_dims(arr2, axis = 0))

  def convert_board_to_input(self, state, color, current = True) :
    if current :
      board = chess.Board(state)
      board.turn = color
      arr = np.zeros((8,8,12), dtype = np.float32)
      arr2 = np.zeros((8,8,10), dtype = np.float32)
      piece_to_value = self.get_piece_to_value(color)
      piece_to_value2 = self.get_piece_to_value(color, False)
      for i in range(64) :
        if(board.piece_at(i) is not None) :
          arr[i//8,i%8,piece_to_value[board.piece_at(i).symbol()]] = 1
      for move in board.legal_moves :
        square = move.to_square
        arr[square//8, square%8, piece_to_value[board.piece_at(move.from_square).symbol()]] = 0.5
        symbol = board.piece_at(move.from_square).symbol()
        if move.promotion is not None :
          arr2[move.promotion-2, move.from_square%8, 9] = 1
        else :
          arr2[square//8, square%8, piece_to_value2[symbol]] = 1
          if(piece_to_value2[symbol] == 1 or piece_to_value2[symbol] == 3 or piece_to_value2[symbol] == 5) :
            piece_to_value2[symbol] += 1
      return (arr, arr2)
    else :
      arr = np.zeros((8,8,12), dtype = np.float32)
      if len(state) == 0 :
        return arr
      board = chess.Board(state)
      board.turn = color
      piece_to_value = self.get_piece_to_value(color)
      for i in range(64) :
        if(board.piece_at(i) is not None) :
          arr[i//8,i%8,piece_to_value[board.piece_at(i).symbol()]] = 1
      return arr
    
  def convert_output_to_probs(self, state, color, policy_output) :
    policy = np.reshape(policy_output, [8,8,10])
    board = chess.Board(state.split("_")[-1])
    board.turn = color
    piece_to_value = self.get_piece_to_value(color,False)
    move_dict = {}
    for move in list(board.legal_moves) :
      to_square = move.to_square
      from_square = move.from_square
      piece_type = piece_to_value[board.piece_at(from_square).symbol()]
      if move.promotion is not None :
        move_dict[move.uci()] = policy[move.promotion-2, from_square%8, 9]
      else :
        move_dict[move.uci()] = policy[to_square//8, to_square%8, piece_type]
        if(piece_type == 1 or piece_type == 3 or piece_type == 5) :
          piece_to_value[board.piece_at(from_square).symbol()] += 1
   # print(list(board.legal_moves))
    move = [item[0] for item in sorted(move_dict.items(), key = lambda x: x[1], reverse = True)][0]
    print(move)
    return move
  
  def get_piece_to_value(self, color, inp = True) :
    if inp :
      if(color == 1) :
        return {
        'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
        'p': 6, 'n':7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
        }
      return {
        'p': 0, 'n': 1, 'b': 2, 'r': 3, 'q': 4, 'k': 5,
        'P': 6, 'N':7, 'B': 8, 'R': 9, 'Q': 10, 'K': 11
      }
    else :
      if(color == 1) :
        return {
        'P': 0, 'N': 1, 'B': 3, 'R': 5, 'Q': 7, 'K': 8
        }
      return {
        'p': 0, 'n': 1, 'b': 3, 'r': 5, 'q': 7, 'k': 8
      }