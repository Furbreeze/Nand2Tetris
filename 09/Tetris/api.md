# Classes

## Main
### function main() : void
### method loop() : void
```
while (!tetris.game_over()) {  
  tetris.tick()
  this.update_display()  
  this.regulate_time()
  this.get_input()
}
```
### method update_display(Tetris tetris) : void
```
# draw gui
# draw field
# print score
```
### method get_input() : char
```
# allowed keys are left, right, up, space
# check for key pressed
# return ascii for key pressed
```

## Tetris
### method tick(int input) : void
```
this.update_gravity()
this.handle_input()
this.clear_lines()
this.update_score()
this.check_game_over()
```
### method update_gravity(int time) : void
### method handle_input(int input) : void
### method clear_lines() : void
### method update_score() : void
### method check_game_over() : bool