# Changelog
## Palackovic Filip - 5BHEL 2023/24

For my changes I had to switch from using impulses like in the original gamefile, to using the coordinates, thus I had to delete some function and implement them
in other ways.

* The boarders were adaptet so that the ball can be thrown from better, without hitting the top. (commit Test)

* Trying to get the ball to jump like flappy bird in a extra file -> deleted later on (commit neue datei fuer versuch)

### Sling Action 

* The function sling_action() was also deletet, because no mouse angle is needed with the game change. (Update 1601)

### Keydowns

A new Keydown-Event was created, to be able to know, when the Space bar was pressed. (Update 1601)

### Ball launch

The function handle_ball_launch was changed completly.  (Update 1601)
This function contains:
* Ball Movement
* Scoring
* Boundaries
* Time


### Boundaries
Boundaries were added around the Basket. The ball bounches of these Boundaries (commit Update1601) (commit 1701)

### Time
A shotclock was implemented. The ball needs to be scored for the shotclock to reset. The time also changes with the amount of buckets made. (commit 1701)
