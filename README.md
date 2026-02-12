# Covid19 War Shooter

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Pygame](https://img.shields.io/badge/Pygame-Game%20Engine-green)


**Covid19 War** is a retro-style arcade shooter developed in **Python** using the **Pygame** library.  
The game challenges players to survive against continuously spawning waves of enemies while collecting recovery points to maintain health. Gameplay focuses on fast movement, continuous shooting, and increasing difficulty through a progressive wave system.

https://github.com/user-attachments/assets/3c443c8b-f644-4fb1-9d52-cccff83bb661

---

<!-- ## Gameplay Preview -->
<!-- *(Add screenshots or GIFs here)* -->

<!-- --- -->

## Features
- Retro arcade-style gameplay  
- Full **4-directional movement** with simultaneous shooting  
- Progressive **wave-based enemy spawning**  
- Randomized scoring rewards  
- Randomized health recovery system  
- Increasing difficulty with each wave  
- Score tracking system  

---

## Gameplay Mechanics

### Player Movement
The player can move freely in four directions:
- Left  
- Right  
- Forward  
- Backward  

Movement can be performed simultaneously with shooting, allowing continuous combat engagement.

### Shooting System
The player continuously fires projectiles to eliminate enemies. Projectile collisions with enemies remove them from the screen and award points.

### Wave System
The game progresses through **waves**, where:
- Each new wave spawns **more enemies** than the previous one  
- Enemy density and difficulty gradually increase  

---

## Scoring System
Each enemy defeated grants a **random score reward**:
- Minimum score: **10 points**
- Maximum score: **120 points**

---

## Recovery System
Health recovery items occasionally appear in the game. When collected, they restore a random amount of health:
- Minimum recovery: **2 points**
- Maximum recovery: **15 points**

---

## Controls

| Action | Keyboard | Controller |
|------|------|------|
| Move Left | Left Arrow | -LX |
| Move Right | Right Arrow | +LX |
| Move Forward | Up Arrow | +LY |
| Move Backward | Down Arrow | -LY |
| Shoot | Spacebar | A |

*(Controls may vary depending on controller support.)*

---

## Installation

### Requirements
- Python 3.x
- Pygame

### Install dependencies
```bash
pip install pygame

# Run
python covidWarRemaster.py
```

## Future Improvements
- Boss enemies for milestone waves  
- Weapon upgrade system  
- Difficulty scaling based on player performance  
- Leaderboard and high-score saving  
- Additional visual effects and animations  
- Multiplayer or co-op mode  




