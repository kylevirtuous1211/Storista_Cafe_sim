# Brainstorm notes

The running record of the Storista Café brainstorm: what is decided, what is only proposed, and what is still open.
The design for the first milestone, the neighbors, is in [docs/superpowers/specs/2026-11-25-neighbors-design.md](superpowers/specs/2026-11-25-neighbors-design.md).
Nothing is built yet.

## The idea

A cozy game about owning a little coffee shop in a wooden cabin, in full 3D with cute characters.
You start with an empty shop and make it yours, win customers, get to know the neighbors and explore the neighborhood.
The shop keeps a gentle idle side, so it can keep going while you are away.
Free decorating is a mechanic people know from life-sim games; the look and the characters stay our own.

## Decided

### The look: Storybook Cabin (2026-11-22)

| Outside at golden hour | Inside on a rainy evening |
| --- | --- |
| ![Hand-painted log cabin coffee shop in a forest clearing at golden hour](concept-art/storybook_exterior.jpg) | ![Inside the log cabin café on a rainy evening, with warm lamps, regulars and a sleeping cat](concept-art/storybook_interior.jpg) |

- A log cabin in the woods, painted like a picture book: hand-painted textures with soft brush strokes, warm lamplight, weather and time of day.
- You walk around as the owner, inside and out, with the camera following behind you.
- Round-faced storybook people and animals, about three heads tall.
- It was picked over three other looks; see [the four looks compared](#the-four-looks-compared-2026-11-22).

### The moments to look forward to, in order (2026-11-22)

1. Customers: talking with them, and winning new ones.
2. Decorating: starting from an empty coffee shop and making it cute through play.
3. Neighbors and the map: neighbors to get to know, and an open world to explore.

### Customer visits: both, mixed (2026-11-23)

- Everyday orders are quick, so the focus stays on the people.
- Special moments, such as a regular's birthday, a new recipe or a picky visitor, open a hands-on brewing mini-game.

### Neighbors are driven by a real LLM (2026-11-23)

The idea, in its original words:

> 可以後端接真的的 LLM，可能 qwen 3.5，這樣可以直接 evaluate，但每個人都要有固定好的 persona 還有興趣，user 可以慢慢認識鄰居還有他們的喜好，鄰居的喜好度會影響心情，心情會影響各個決定，像是要不要來咖啡店或是像其他鄰居宣傳咖啡店的可能性，類似 social graph 的感覺

In English:

- A real LLM runs behind the neighbors, maybe Qwen 3.5, so it can evaluate interactions directly.
- Every neighbor has a fixed persona and fixed interests.
- The player gets to know the neighbors and what they like, little by little.
- How much a neighbor likes you shapes their mood, and their mood shapes their decisions: whether to come to the café, and how likely they are to tell other neighbors about it.
- It works like a social graph.

This makes word of mouth through the neighbors' friendships the way the café wins new customers, so moments 1 and 3 become one system.

### Talking with neighbors: both, and start with the neighbors (2026-11-25)

- The player taps one of three suggested replies, or types their own line at any time.
- This was the recommended option; the answer on the review page was "let's go", sent together with the neighbor idea again, so it stands until changed.
- "Let's go" also moved the round 2 and round 3 proposals below from proposals to the working direction, to be confirmed by approving the design doc.
- The first milestone builds the neighbors before any 3D.

## Working direction, confirmed by approving the design doc

### The café loop (round 2, 2026-11-22)

Explore the valley, meet neighbors, welcome new customers, serve and befriend them, earn and unlock decor, then decorate the cabin.
A cuter café draws new faces and opens new areas, and the loop starts again.

- Single-player: neighbors are characters in the game, and online play could come much later.
- The open world starts as one hand-built valley (forest paths, a stream, a meadow, neighbors' homes, a village square) that opens up as the café grows.
- A hired helper serves simple orders while you are out, which keeps a little of the idle feel.
- Days, weather and seasons, with an in-game day of about 20 minutes.

### How a neighbor works (round 3, 2026-11-23)

- The LLM talks and scores; the game keeps the numbers.
  The LLM answers in the neighbor's voice and scores each interaction with a small number and a reason, for example "she felt listened to, +2".
  Affinity, mood and every probability live in the game, and game rules decide visits and word of mouth.
  That keeps the numbers consistent, saveable, tunable and testable, stops one clever sentence from tricking a neighbor, and means the game never waits on the model to make a decision.
- Every neighbor has a fixed persona card: personality, way of speaking, interests, liked and disliked drinks, snacks and decor, daily routine, and friendships.
  The LLM performs only within the card, so a neighbor stays the same person every day.
  Cards are drafted with AI help and reviewed by hand.
- Neighbors remember you.
  Each night the day's interactions are condensed into a few memories they can bring up later ("yesterday's cinnamon roll was lovely").
- A neighbor notebook fills in as you discover likes, birthdays and friendships, so getting to know someone shows as progress.
- Word of mouth follows friendships.
  Each night a happy neighbor may tell their friends about the café, and friends who hear good things are more likely to visit.
  A bad mood only means fewer visits, never bad-mouthing, to keep the game cozy.
- Decor ties into interests.
  The plant lover is happier among plants and the bookworm likes a reading nook, so decorating becomes a way to win particular customers.
- The model runs on the same PC through llama.cpp's server, reached over local HTTP like ComfyUI.
  The first candidate is Qwen3.5-35B-A3B, a mixture of experts with about 3B active parameters, so it answers fast; its 4-bit file is 22 GB.
  The fallback is Qwen3.5-9B, 5.7 GB at 4-bit.
  llama.cpp can force JSON output, which keeps the scores well-formed.
  The GPU has 48 GB, and ComfyUI is not needed while playing.

## Open questions

- The first cast of neighbors is drafted in the design doc and waits for review.
- Still ahead, each in its own milestone: what the neighbors look like, how decorating works, what there is to do in the valley, and how the AI asset pipeline joins this repo.

## The four looks compared (2026-11-22)

All concept art was made locally with Z-Image-Turbo in ComfyUI.
Treat it as mood boards, not game screenshots.

### A · Pocket Diorama

| The whole shop at a glance, front wall cut away | Decorating mode: furniture snaps to a grid |
| --- | --- |
| ![Cutaway miniature wooden coffee hut on a round mossy base with chibi customers](concept-art/diorama_overview.jpg) | ![Isometric café room in decorating mode with a glowing placement grid](concept-art/diorama_decorate.jpg) |

Your hut as a tiny toy world you could hold in your hand: pastel colors, rounded toy-like shapes, and a fixed camera from above.
Best at idle play and grid decorating, with less feeling of being there.

### B · Storybook Cabin (picked)

The images are under [The look](#the-look-storybook-cabin-2026-11-22).
Best at feeling present: rain on the windows, regulars by the stove, a garden to tend outside.
The catch is lighting, weather and a whole forest to build, and it is harder to watch the whole shop during idle play.

### C · Felt and Clay

| Plush regulars at a clay counter | Outside: patchwork hills, felt trees, yarn clouds |
| --- | --- |
| ![Felt and clay coffee hut set with plush animal customers and a plush fox barista](concept-art/felt_interior.jpg) | ![Wooden coffee hut with a felt roof on a patchwork fabric hill](concept-art/felt_exterior.jpg) |

A handmade stop-motion set where everything looks touchable, with plush-toy animal characters.
AI props would need one shared felt and clay material to match each other.

### D · Toon Café

| After-school rush: latte art, sparkles, chatty regulars | A hut by a country train stop in cherry blossom season |
| --- | --- |
| ![Cel-shaded coffee hut interior with a chibi barista pouring latte art for students](concept-art/toonink_interior.jpg) | ![Cel-shaded wooden coffee hut beside a country train platform under cherry blossom trees](concept-art/toonink_exterior.jpg) |

A bright cel-shaded look with bold ink outlines and expressive chibi characters.
Unreal would need a custom toon material and outline effect, and AI props would need restyling to flat shading.

### Side by side

These were estimates of how each look plays with Unreal and the AI asset pipeline.

| | A · Diorama | B · Storybook | C · Felt and Clay | D · Toon |
| --- | --- | --- | --- | --- |
| Idle shop that runs itself | Best | Okay | Good | Good |
| Decorating your hut | Best, on a grid | Good, walk in and place | Good | Good |
| Feeling of being there | Light | Best | Good | Good |
| Cute characters | Good | Good | Best | Best |
| Fit with AI-made props | Best | Good | Good, with a shared material | Needs restyling |
| Effort to build | Lowest | Highest | Medium | Medium |

### How the concept art was made

`tools/concept_art.py` holds every prompt and chosen seed, and re-renders the images with the local ComfyUI.
Each scene was rendered with two seeds, and the better image was kept.
Two earlier toon attempts were dropped.
The first came out as a flat 2D illustration, and the second drifted toward the look of a well-known life-sim game, so the toon look got thick ink outlines and a setting of its own.
