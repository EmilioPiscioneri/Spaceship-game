# Spaceship-game
 A python game using pgame. Just small project, learning python.

 ## Known bugs/limitations
 - The movement of the player spaceship increases when travelling in diagional direction (overall).
 - The hitbox is like an axis-aligned bounding boxes (AABB). Doesn't support rotations
 - You can go out of the map when going into the right wall by going right and then stopping. You can leave tho. This can be done by adding padding of 1 pixel.
 - I chose not dividing movement by 2 when travelling diagonally this was too slow. This means it is faster to travel diagonally in 2D.
 - You can't stop on diagonal movement. The player picks a standard direction (N,E,S,W)
 - Firing towards player from enemy doesn't take into account player rotations to calculate midpoint, however, you can't notice this with how fast the projectile is
 - You can go into enemies. This was a design choice as I thought it was more risky to go right into enemies. Also, I can't be stuffed preventing collisions.
 - There is no retry button or key.

 - When a new level loads (including first). The enemy fires straight away. This is a bug
