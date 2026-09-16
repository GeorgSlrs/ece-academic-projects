# Frogger Arcade Game

An early Python team project recreating the road-and-river crossing mechanics of Frogger with Turtle graphics and a Tkinter menu. The player uses the arrow keys to avoid traffic, ride logs and turtles, and reach five homes while managing lives and a time limit.

The game models the player, vehicles, floating platforms and goals as classes. Its update loop moves objects, detects collisions, updates the displayed lives/time and resets the round after success or lost lives.

## Files

- [ΤΟ ΠΡΟΓΡΑΜΜΑ/](%CE%A4%CE%9F%20%CE%A0%CE%A1%CE%9F%CE%93%CE%A1%CE%91%CE%9C%CE%9C%CE%91/) — game source, `menu.py`, required GIF sprites, background and menu image, plus a run guide.
- [frogger.py](frogger.py) — additional source copy at the project root; its image references are relative to the working directory.
- Team report, presentation and installation documents — design and coursework context.
- `ΠΡΟΣΩΠΙΚΕΣ ΕΚΘΕΣΕΙΣ/` — archived individual contribution reports.

## Run

Use Python 3 with Tk/Tkinter support; the game scripts require no third-party Python packages. Change into `ΤΟ ΠΡΟΓΡΑΜΜΑ` and run:

```bash
python menu.py
```

If the menu's platform-specific launcher does not open the game, run `python frogger.py` from the same directory. Keep the image assets beside the scripts.

This was team coursework. My documented contribution included initial code, team coordination, integration, debugging/testing and audio work. The preserved source and reports reflect an early learning project and are not a claim of sole authorship of the complete game.
