"""
CSSE1001 Assignment 2
Semester 2, 2020
"""
from a2_support import *

# Fill these in with your details
__author__ = "{{user.name}} ({{user.id}})"
__email__ = ""
__date__ = ""


# Write your code here

class GameLogic:
    """Contains all the game information and how the game should play out.
    """

    def __init__(self, dungeon_name="game1.txt"):
        """Constructor of the GameLogic class.

        Parameters:
            dungeon_name (str): The name of the level.
        """
        self._dungeon = load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        self._dictionary = {}
        self._dungeon_name = dungeon_name

        # you need to implement the Player class first.
        self._player = Player(GAME_LEVELS[dungeon_name])

        # you need to implement the init_game_information() method for this.
        self._game_information = self.init_game_information()

        self._win = False

    def get_positions(self, entity):
        """ Returns a list of tuples containing all positions of a given Entity
             type.

        Parameters:
            entity (str): the id of an entity.

        Returns:
            )list<tuple<int, int>>): Returns a list of tuples representing the
            positions of a given entity id.
        """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def get_dungeon_size(self):
        """Returns the width of the dungeon as an integer.
        """
        return self._dungeon_size

    def init_game_information(self):
        """Return a dictionary containing the position and the corresponding
           Entity as the keys and values respectively.

        Returns:
            dict<tuple<int, int>: Entity>
        """

        key = self.get_positions(KEY)
        for i in key:
            self._dictionary[i] = Key()

        door = self.get_positions(DOOR)
        for i in door:
            self._dictionary[i] = Door()

        wall = self.get_positions(WALL)
        for i in wall:
            self._dictionary[i] = Wall()

        moveincrease = self.get_positions(MOVE_INCREASE)
        for i in moveincrease:
            self._dictionary[i] = MoveIncrease(5)

        player = self.get_positions(PLAYER)[0]
        self._player.set_position(player)

        return self._dictionary

    def get_game_information(self):
        """Returns a dictionary containing the position and the corresponding
        Entity

        Returns: self._dictionary(dictionary)
        """
        return self._game_information

    def get_player(self):
        """Returns player object in game

        Returns: Player(object)
        """
        return self._player

    def get_entity(self, position):
        """Returns an Entity at a given position in the dungeon.

        Returns: Entity(str)
        """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """Returns an Entity at a given position in the dungeon.
        """
        entity_direction = self.new_position(direction)
        return self.get_entity(entity_direction)

    def collision_check(self, direction):
        """ Returns False if a player can travel in the given direction,
        they won’t collide

        Parameters: Direction <str>
        """
        entity_direction = self.get_entity_in_direction(direction)
        if entity_direction == None:
            return False
        elif entity_direction.can_collide() == False or entity_direction.can_collide() == None:
            return True
        return False

    def new_position(self, direction):
        """Returns a tuple of integers that represents the new position
        given the direction.

        Parameters: Direction <str>
        """
        pos = self._player.get_position()
        direction = DIRECTIONS[direction]
        x, y = pos[0] + direction[0], pos[1] + direction[1]
        new_position = (x, y)
        return new_position

    def move_player(self, direction):
        """Update the Player’s position to place them one position in the
        given direction.

        Parameters: Direction <str>
        """
        new_pos = self.new_position(direction)
        self._player.set_position(new_pos)

    def check_game_over(self):
        """Return True if the game has been lost and False otherwise.
        """
        if self._player.moves_remaining() == 0:
            return True
        return False

    def set_win(self, win):
        """Set the game’s win state to be True or False.

        Parameters: win <bool>
        """
        self._win = win

    def won(self):
        """Return game’s win state
        """
        return self._win


class GameApp:
    """Acts as a communicator between the GameLogic and the Display.
    """

    def __init__(self):
        """Constructor of GameApp
        """
        self._gamelogic = GameLogic()
        self._display = Display(self._gamelogic.get_game_information(), self._gamelogic.get_dungeon_size())
        self._player = self._gamelogic.get_player()

    def play(self):
        """Handles the player interaction.
        """
        while self._gamelogic.get_player().moves_remaining() != 0:
            self.draw()
            Action = input('Please input an action: ')
            
            #Checking if investigate action was used. If so returns entity in direction or None.
            if Action == INVESTIGATE + ' W' or Action == INVESTIGATE + ' A' or Action == INVESTIGATE + ' S' or Action == INVESTIGATE + ' D':
                self._player.change_move_count(-1)
                split = Action.split()
                info_txt = self._gamelogic.get_entity_in_direction(split[1])
                print(info_txt, 'is on the', split[1], 'side.')
                
                #Checking if last move was used to Investigate the direction
                if self._player.moves_remaining() == 0:
                    print(LOSE_TEST)
                    return
                
            #Checking if action is quit or help
            elif Action == QUIT:
                Quit = input('Are you sure you want to quit? (y/n): ')
                if Quit == 'y':
                    return
                elif Quit == 'n':
                    continue
            elif Action == HELP:
                print(HELP_MESSAGE)

            #Checking if player runs out of moves
            elif self._player.moves_remaining() == 1:
                print(LOSE_TEST)
                return
            
            #Checking if player has input direction
            elif Action == 'W' or Action == 'A' or Action == 'S' or Action == 'D':
                #Checking if collision is False
                if self._gamelogic.collision_check(Action) == False:
                    self._player.change_move_count(-1)
                    self._gamelogic.move_player(Action)

                    #Checking if collided with a Key
                    if self._gamelogic.get_positions(KEY)[0] == self._player.get_position():
                        self._gamelogic.get_game_information()[self._gamelogic.get_positions(KEY)[0]].on_hit(self._gamelogic)
                        
                    #Checking if collided with a Door
                    elif self._gamelogic.get_positions(DOOR)[0] == self._player.get_position():
                        self._gamelogic.get_game_information()[self._gamelogic.get_positions(DOOR)[0]].on_hit(self._gamelogic)
                        if self._gamelogic.won() == True:
                            print(WIN_TEXT)
                            return
                        
                    #Checking game level to determine if on hit for moveincrease is required
                    elif self._gamelogic._dungeon_name == 'game2.txt' or self._gamelogic._dungeon_name == 'game3.txt':
                        if self._gamelogic.get_positions(MOVE_INCREASE)[0] == self._player.get_position():
                            self._gamelogic.get_game_information()[self._gamelogic.get_positions(MOVE_INCREASE)[0]].on_hit(self._gamelogic)

                #In this case collision is True.
                else:
                    self._player.change_move_count(-1)
                    print(INVALID)

            #Prints invalid if Any other command is inputed
            else:
                print(INVALID)


    def draw(self):
        """Displays the dungeon with all Entities in their positions.
        """
        self._display.display_game(self._gamelogic.get_player().get_position())
        self._display.display_moves(self._gamelogic.get_player().moves_remaining())


class Entity:
    """A generic Entity within the game.
    """

    def __init__(self):
        """Constructor of the Entity class.
        """
        self._id = 'Entity'
        self._count = 1

    def get_id(self):
        """Returns a string that represents the Entity’s ID.

        Returns:
            Entity Id(str)
        """
        return self._id

    def set_collide(self, collidable):
        """Sets the collision state of the Entity to be True

        Parameters:
            collidable (bool): state of the Entity.

        """
        self._count == 1
        self.can_collide()

    def can_collide(self):
        """Returns True if the Entity can be collided with (another
        Entity can share the position that this one is in) and False
        otherwise.
        """
        if self._count == 1:
            self._count += 1
            return True
        else:
            return False

    def __str__(self):
        """Returns the string representation of the Entity.
        Returns:
            Entity(str) - string representation
        """
        return """Entity('{}')""".format('Entity')

    def __repr__(self):
        """ Same as str(self).
        """
        return self.__str__()


class Wall(Entity):
    """A special type of an Entity within the game that connot be collided with
    """

    def __init__(self):
        """Constructor of the Wall class.

        Parameters:
            None.
        """
        self._id = WALL
        self._count = 1

    def set_collide(self, collidable):
        """Sets the collision state of the Wall to be False

        Parameters:
            collidable (bool): state of the Wall.

        """
        self._count == 1
        self.can_collide()

    def can_collide(self):
        """Returns True if the Wall can be collided with and False
        otherwise.
        """
        if self._count == 1:
            self._count += 1
            return False
        else:
            return True

    def __str__(self):
        """Returns the string representation of the Wall.

        Returns:
            Wall Id(str) - string representation of Wall
        """
        return """Wall('{}')""".format(WALL)

    def __repr__(self):
        """ Same as str(self).
        """
        return self.__str__()


class Item(Entity):
    """A special type of entity within the game. Is an abstract class
    """

    def on_hit(self, game):
        """Raises NotImplementedError
        """
        raise NotImplementedError

    def __str__(self):
        """Returns the string representation of the Item.

        Returns:
            Item Id(str) - string representation of Item
        """
        return """Item('{}')""".format('Entity')

    def __repr__(self):
        """ Same as str(self).
        """
        return self.__str__()


class Key(Item):
    """A Key is a special type of Item within the game that can be collided with

    Parameters: None
    """

    def __init__(self):
        """Constructor of the Key class.

        Parameters:
            None.
        """
        self._id = KEY
        self._count = 1

    def __str__(self):
        """Returns the string representation of the Key.

        Returns:
            Key Id(str) - string representation of Key
        """
        return """Key('{}')""".format(KEY)

    def __repr__(self):
        """ Same as str(self).
        """
        return self.__str__()

    def on_hit(self, game):
        """When the player takes the Key the Key should be added to the
        Player’s inventory. The Key should then be removed from the dungeon
        once it’s in the Player’s inventory.
        """
        game.get_player().add_item(self)
        position = game.get_positions(KEY)
        game.get_game_information().pop(position[0])


class MoveIncrease(Item):
    """A special type of Item within the game that can be collided with
    """

    def __init__(self, moves=5):
        """Constructor of the Entity class.

        Parameters:
            Move(int): number of extra moves the Player will be granted
            when they collect this Item.
        """
        self._id = MOVE_INCREASE
        self._count = 1
        self._moves = moves

    def __str__(self):
        """Returns the string representation of the MoveIncrease.

        Returns:
            MoveIncrease Id(str) - string representation of MoveIncrease
        """
        return """MoveIncrease('{}')""".format(MOVE_INCREASE)

    def __repr__(self):
        """ Same as str(self).
        """
        return self.__str__()

    def on_hit(self, game):
        """When the player hits the MoveIncrease (M) item the number
        of moves for the player increases and the M item is removed from
        the game
        """
        game.get_player().change_move_count(self._moves)
        position = game.get_positions(MOVE_INCREASE)
        game.get_game_information().pop(position[0])


class Door(Entity):
    """The Door Entity can be collided with (The Player should be able to
    share its position with the Door when the Player enters the Door.)
    """

    def __init__(self):
        """Constructor of the Door class.

        Parameters:
            None.
        """
        self._id = DOOR
        self._count = 1

    def __str__(self):
        """Returns the string representation of the Door.

        Returns:
            Door Id(str) - string representation of Door
        """
        return """Door('{}')""".format(DOOR)

    def __repr__(self):
        """ Same as str(self).
        """
        return self.__str__()

    def on_hit(self, game):
        """If the Player's inventory contains a Key Entity then this method
        should set the 'game over' state to be True.
        """
        try:
            game.get_player().get_inventory()[0]
            game.set_win(True)
        except IndexError:
            print("You don't have the key!")


class Player(Entity):
    """A Player is a special type of an Entity within the game that can be
    collided with.
    """

    def __init__(self, move_count):
        """Constructor of the Key class.

        Parameters:
            move_count(int): number of moves a Player can have for the
            given dungeon they are in.
        """
        self._id = PLAYER
        self._count = 1
        self._inventory = []
        self._move_count = move_count

    def set_position(self, position):
        """ Sets the position of the Player

        Parameters: position(tuple) - position of the player
        """
        self._position = position
        (self._x, self._y) = self._position

    def get_position(self):
        """Returns a tuple of ints representing the position of the Player. If the Player’s position hasn’t been set yet then this method should
        return None.
        """
        try:
            return self._position
        except AttributeError:
            return None

    def change_move_count(self, number):
        """number to be added to the Player’s move count.
        Parameters: number(int) - the number added to the move count
        """
        self._move_count += number

    def moves_remaining(self):
        """Returns an int representing how many moves the Player has
        left before they reach the maximum move count.
        """
        return self._move_count

    def add_item(self, item):
        """Adds the item to the Player’s Inventory

        Parameters: item(Entity) - item to be added to the inventory

        """
        self._inventory.append(item)

    def get_inventory(self):
        """Returns a list that represents the Player’s
        inventory. If the Player has nothing in their inventory then
        an empty list should be returned.
        """
        return self._inventory

    def __str__(self):
        """Returns the string representation of the Player.

        Returns:
            Player Id(str) - string representation of Player
        """
        return """Player('{}')""".format(PLAYER)

    def __repr__(self):
        """ Same as str(self).
        """
        return self.__str__()


def main():
    GameApp().play()


if __name__ == "__main__":
    main()
