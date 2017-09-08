# Game of Tanks for RL agents

A simple game built with the help of [pygame](https://www.pygame.org/news) library where two tanks battle each other to win. Both the tanks can be either controlled by reinforcement-learning agent(s) or one of them can be controlled by a human player in a 1v1 human-vs-bot matchup. 

## Milestones

1. Creating a simple UI where the welcome screen with some text is shown
2. Welcome screen stays until a specific key is pressed, and then the tanks are rendered
3. Control a tank with manual agent
4. Control a tank with a random/rule-based (non-learning) agent
5. Control a tank with a reinforcement learning agent
6. Train two instances of the same RL agent against each other for a large number of iterations
7. Save the generations of the RL agents after every n iterations and compare the performances of strategies learnt over the iterations

## Interesting scenarios

1. HP pool for the tanks instead of single-hit kill
2. Projectiles can do variable damage depending upon when the last projectile was fired
3. Projectiles have spread (reduced accuracy) depending upon when the last projectile was fired
4. Tanks have speed and bullet budget
5. Field is not open, some destructable walls are randomly scattered
