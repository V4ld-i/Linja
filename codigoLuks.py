from typing import List, Tuple
from PIL import Image, ImageDraw
from copy import deepcopy
from IPython.display import display, HTML
import math

class BoardLinja:
    
    #Inicializa el tablero
    def _init_(self, board: List[List[str]]):
        self.board = board
    
    #Método que compara tableros
    def _eq_(self, other) -> bool:
        return self.board == other.board
    
    #Devuelve el tablero.
    def getMatrix(self) -> List[List[str]]:
        return [''.join(row) + '\n' for row in self.board]
    
    #Establece el tablero
    def setMatrix(self, board: List[List[str]]):
        self.board = deepcopy(board)
    
    #Coloca una ficha donde se le indique
    def placeTile(self, row: int, col: int, tile: str):
        self.board[row][col] = tile
    
    #Elimina la ficha en la casilla indicada
    def deleteTile(self, row: int, col: int):
        if self.board[row][col] != "V":
            row_list = list(self.board[row])
            row_list[col] = "V"
            self.board[row] = ''.join(row_list)
            
    #Crea el tablero visual con los PNGs
    def getVisualMatrix(self) -> Image.Image:
        cell_size = 50
        board_size = (len(self.board[0]) * cell_size, len(self.board) * cell_size)
        visual_matrix = Image.new("RGB", board_size, color="white")

        for row_index, row in enumerate(self.board):
            for col_index, cell in enumerate(row):
                cell_image = Image.open("CasillaRoja.png").resize((cell_size, cell_size)) if cell == "R" else \
                             Image.open("CasillaNegra.png").resize((cell_size, cell_size)) if cell == "N" else \
                             Image.open("CasillaVacia.png").resize((cell_size, cell_size))

                visual_matrix.paste(cell_image, (col_index * cell_size, row_index * cell_size))

        return visual_matrix

    def showVisualMatrix(self, visual_matrix):
        display(visual_matrix)
        
    #Función de utilidad
    def utility(self) -> int:
        PointsR = 0
        PointsB = 0
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if self.board[row][col] == "R":
                    PointsR += {0: 5, 1: 3, 2: 2, 3: 1}.get(row, 0)
                elif self.board[row][col] == "N":
                    PointsB += {7: 5, 6: 3, 5: 2, 4: 1}.get(row, 0)
                    
        return PointsR - PointsB
    
    #Devuelve una lista de todas las filas a las que se puede mover
    def isAvailable(self) -> List[int]:
        available_rows = []
        for row in range(len(self.board)):
            if "V" in self.board[row]:
                available_rows.append(row)
        return available_rows
    
    def moveCanBeMade(self, player):
        # Implementa la lógica necesaria para verificar si un movimiento es posible
        # Puedes adaptar esto según los detalles específicos de tu implementación del juego
        return True  # Por ahora, simplemente devuelve True como ejemplo
        
    #Devuelve el ID del jugador ganador, o 0 si es un empate
    def endGame(self) -> int:
        puntos_utilidad = self.utility()
        if all(row.count("R") > 0 for row in self.board[:4]):
            if puntos_utilidad == 0:
                return 3
            elif puntos_utilidad > 0:
                return 1
            else:
                return 2
        return 0

    #Devuelve el número de movimientos del turno extra
    def numMovs(self, row: int) -> int:
        tiles = 0
        for tile in self.board[row]:
            if tile != "V":
                tiles += 1
        return tiles
    
    # Método que devuelve una lista con todos los movimientos posibles de una ficha
    def obtenerMov(self, row: int, col: int, playerID: int, numMov: int, numFilasSeg: int) -> List[List[int]]:
        movimientos_posibles = []

        if playerID == 1:
            direccion = -1
        else:
            direccion = 1

        nueva_fila = row + (direccion * numMov)

        # Verifica si la nueva fila está dentro de los límites del tablero
        if 0 <= nueva_fila < len(self.board):
            # Agrega todas las casillas vacías de la fila a la lista de movimientos posibles
            for nueva_col in range(len(self.board[nueva_fila])):
                if self.board[nueva_fila][nueva_col] == "V":
                    movimientos_posibles.append([nueva_fila, nueva_col])

        return movimientos_posibles
    
	#TODO Comprobar esto
    #Método que mueve una ficha a la casilla indicada
    def moverFicha(self, playerID: int, ficha_origen: List[int], casilla_destino: List[int]) -> int:
        try:
            row_origen, col_origen = ficha_origen
            row_destino, col_destino = casilla_destino

            if playerID not in [1, 2]:
                raise ValueError("Error en el ID del jugador")

            if not (0 <= row_origen < len(self.board) and 0 <= col_origen < len(self.board[0])):
                raise ValueError("Error en la fila o columna de la ficha de origen")

            if not (0 <= row_destino < len(self.board) and 0 <= col_destino < len(self.board[0])):
                raise ValueError("Error en la fila o columna de la casilla destino")
            
            ficha_actual = self.board[row_origen][col_origen]

            if ficha_actual not in ["R", "N"]:
                raise ValueError("Error: No hay ficha para mover en la casilla de origen")

            if self.board[row_destino][col_destino] != "V":
                raise ValueError("Error: La casilla destino no está vacía")

            # Realiza el movimiento
            self.deleteTile(row_origen, col_origen)
            row_destino_list = list(self.board[row_destino])
            row_destino_list[col_destino] = ficha_actual
            self.board[row_destino] = ''.join(row_destino_list)

            return 0
        except ValueError as e:
            print(f"Error en el movimiento: {str(e)}")
            return 1
    
    #Método de MiniMax con poda alfa-beta
    def miniMax(self, currentLevel: int, maxLevel: int, player: int, alpha: int, beta: int, stop: bool) -> Tuple[List[List[str]], int, bool]:
        matriz = self.getMatrix()

        successorMatrices = []

        if (not self.moveCanBeMade(player) or currentLevel == maxLevel):
            return (self.board, self.utility(), stop)

        bestMatrix = None

        if player == 2:
            maxValue = -math.inf  # alpha

            for i in range(len(successorMatrices)):
                mat = BoardLinja(successorMatrices[i])
                _, utility, stop = self.miniMax(currentLevel + 1, maxLevel, 1, alpha, beta, stop)

                if utility > maxValue:
                    maxValue = utility
                    bestMatrix = successorMatrices[i]

                alpha = max(alpha, maxValue)
                if maxValue >= beta:
                    return (bestMatrix, maxValue, stop)

        else:
            minValue = math.inf  # beta

            for i in range(len(successorMatrices)):
                mat = BoardLinja(successorMatrices[i])
                _, utility, stop = self.miniMax(currentLevel + 1, maxLevel, 2, alpha, beta, stop)

                if utility < minValue:
                    minValue = utility
                    bestMatrix = successorMatrices[i]

                beta = min(beta, minValue)
                if minValue <= alpha:
                    return (bestMatrix, minValue, stop)

        return (bestMatrix, self.utility(), stop)
    
    #Función de funcionamiento de minimax
    def performActionMinMax(self, player: int):
        matrizB = self.getMatrix()

        tmpMatriz = [row[:] for row in matrizB]

        # Profundidad que desees, por ejemplo 2
        depth = 2

        matrizoptima = tmpMatriz
        stop = False
        currentLevel = 0
        itera = 0

        while not stop and itera <= 3:
            tmpMatrizB = Boardlinja(tmpMatriz)
            (matrizoptima, valoroptimo, stop) = self.miniMax(currentLevel, depth, player, -math.inf, math.inf, stop)
            itera += 1

        # En este punto, matrizoptima contiene la matriz resultante después de aplicar MiniMax
        # Puedes realizar cualquier acción que necesites con esta matriz
        # Por ejemplo, imprimir la matriz resultante

        # También puedes devolver la matriz optima o cualquier otro resultado que necesites
        return matrizoptima
    
    def AIAction(self, player: int):
        global AIReadyToMove

        matriz = self.getMatrix()

        # Llamada a performActionMinMax
        result_matrix = self.performActionMinMax(player)

        AIReadyToMove = False

        # Puedes cambiar esta línea según lo que necesites devolver
        return result_matrix
