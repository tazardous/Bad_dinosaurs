# Dino Dinner Dash

A gentle platformer for little learners, starring Kellan, Diana and their dog
Bernie (all in dino hoods) and an original family of naughty dinosaurs. It is
meant for kids around 4 to 6 who love learning: nobody can lose, there are no
lives, and every wrong answer is just a "try again".

One self-contained `index.html`, no build step. The only network request is the
Press Start 2P font from Google Fonts; offline it falls back to a system
monospace font. All characters, art, levels and music are original.

## The story

Baby Pip has been very naughty and scattered the family's dinner all over the
valley. Help Kellan or Diana (and Bernie) find Baby Pip, Mama Spike, Papa Rocko
and Gramps, and bring everyone home for dinner. Professor Pebbles guards a rock
gate in every level. Answer his question and the gate opens.

## What it teaches

| Level | Topic | Easy (about age 4) | Harder (about age 6) |
|-------|-------|--------------------|----------------------|
| 1 ABC Meadow | Letters | find a letter, first letter of a picture | match big to small letters, what letter comes next |
| 2 Count Cave | Numbers | count 1 to 6 things, what number is next | count to 10, add numbers, skip counting by 2, 5, 10 |
| 3 Shape Swamp | Shapes | circle, square, triangle, star, heart | adds rectangle, oval, diamond, hexagon; name the shape; count the sides |
| 4 Color Canyon | Colors | find a color, finish an AB pattern | more colors, mixing colors, harder patterns |
| 5 Dino Den | Mixed | one of each topic | the harder version of each |

Questions are picked at random, so every play is a little different. The
question is read out loud with the browser's built-in voice (tap the panel to
hear it again; the TALK button turns the voice off). After a wrong answer a
hint appears, and after two the right answer glows. A star is earned for each
gate answered correctly on the first try.

## Playing

| Action | Keyboard | Touch |
|--------|----------|-------|
| Walk | Left and Right arrows (or A and D) | ◀ ▶ |
| Jump / choose / continue | Space, Z or Up | JUMP, or tap the card |
| Pick an answer | Left and Right, then Space | tap the answer card |
| Pause | P or Esc | II |
| Music and sound | M | ♪ |
| Voice | V | TALK |

Pick Kellan or Diana and EASY or HARDER on the title screen. Choices are saved.

- **Berries** are just for fun. **Critters** can be bopped by jumping on them; if
  you bump into one from the side you only get pushed back.
- **Falling in a pit** is never a problem: Bernie catches you in a bubble and you
  float back to the last green flag.
- **Mushrooms** are springs that reach the high ledges.

## Deploy

Settings -> Pages -> Deploy from a branch -> main -> / (root). Then open the URL
in Chrome on the phone and use the menu to Add to Home screen. The installed app
opens full screen in landscape. Everything is relative-pathed.

## Making levels and questions

Levels are in `LEVELS` at the top of `index.html`: width in tiles, pits
(`[x, width]`), floating platforms (`[x0, x1, row]`), gate positions, critters,
springs, flags and which question types each gate asks. Keep pits at 3 tiles or
less, put the last gate 6 tiles from the end, and keep platforms away from gates.
Question types live in `GEN`; each returns the prompt, a picture, three choices
and the right answer. `diff` is 0 for easy and 1 for harder.

## Testing

`tests/run.py` loads the game in headless Chromium and plays every level at both
difficulties with a bot (answering the first gate wrong on purpose), checks that
falling into a pit respawns, that tapping an answer card works, and runs a real-time
session with the keyboard. `tests/shots.py` saves screenshots of every screen
and question type.

```
pip install playwright
python -m playwright install chromium
python tests/run.py
```

## Updating

Edit, bump `CACHE` in `sw.js`, push. Without the version bump the phone keeps
serving the cached copy.
