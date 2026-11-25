# The neighbors: design for milestone 1

Status: draft for review, 2026-11-25.
It turns the [brainstorm notes](../../brainstorm-notes.md) into something buildable.
The whole game is too big for one design, so it is built in milestones.
This document designs the first milestone in full and the later ones only as a direction.

## Intent

Storista Café is a cozy single-player 3D game about owning a little coffee shop in a hand-painted log cabin in the woods.
Its heart is the neighbors.
Each one is a consistent person with a fixed persona, interests and friendships, voiced by a local LLM, and you get to know them little by little.
How a neighbor feels about you decides whether they come to the café and whether they tell their friends about it.
So winning new customers means making friends, and the café's reputation travels along the village's social graph.

The project owner ranked the moments they look forward to: first the customers (talking with them and winning new ones), then decorating from an empty shop, then neighbors and an open world to explore.
The LLM-driven neighbors were the owner's own idea.
On 2026-11-25 they sent it again with "let's go", as the thing to start with.
So milestone 1 builds the neighbors before any 3D.
It is the part the owner cares about most, the part with the most risk, and the part every later milestone plugs into.

## Milestones

1. **The neighbors** (this document): the neighbor brain as a local service, five neighbors, serving and talking, nights with memories and word of mouth, a playtest page, and an evaluation suite.
2. **The cabin**: a new Unreal 5.8 project in this repo with the storybook cabin and its clearing, the owner walking around, and neighbors walking in and talking through the brain.
3. **Decorating**: start from an empty cabin and furnish it, with decor feeding the neighbors' moods.
4. **Days and the helper**: day and night, weather, seasons, a hired helper who keeps the café open while you are away, and more neighbors.
5. **The valley**: forest paths, a stream, the neighbors' homes and a village square, opening up as the café grows.

Each later milestone gets its own design pass when it starts, because questions such as how decorating works and what the valley holds are still open.

## Decided

- The look is Storybook Cabin (2026-11-22); it matters from milestone 2.
- The game is single-player, and the neighbors are characters in it.
- Customer visits are mixed: everyday orders are quick, and special moments open a hands-on brewing mini-game in a later milestone.
- A real local LLM drives the neighbors, who have fixed personas and interests (the owner's idea, 2026-11-23).
  Affinity shapes mood, and mood shapes decisions such as visiting the café and recommending it to friends, like a social graph.
- The LLM talks and scores, and the game owns the numbers.
- The player talks both ways: tap one of three suggested replies, or type their own line at any time.
  This was the recommended option.
  The owner answered "let's go" instead of picking, so it stands until they say otherwise.
- The round 2 and round 3 proposals in the brainstorm notes stand as the direction for the same reason, and approving this document confirms them.

## Goals for milestone 1

Milestone 1 is done when all of these are true:

- In a playtest page you can play day after day with five neighbors.
  You serve each visitor a drink, talk by tapping a suggestion or typing, end the day, and see what each neighbor remembers and who told whom about the café.
- New customers arrive because a friend told them, so you can watch the social graph carry the café's reputation.
- Neighbors stay in character and speak Traditional Chinese as used in Taiwan.
  They bring up earlier days, and they share more about themselves as they grow fond of you.
- The numbers behave.
  Kind, attentive talk raises affinity, and rude talk lowers it a little.
  Attempts to talk the scorer into points earn nothing, and repeating the same chat earns less each time.
  The rules are reproducible: the same save, seed, player actions and model answers give the same numbers.
- The brain's HTTP API is ready to be the contract the Unreal game uses in milestone 2.
- End-to-end tests against the real model, rule tests, typecheck and lint all pass.
- An evaluation report shows the model's latency and behavior.

## Non-goals for milestone 1

- Any 3D, art or character design.
- Decorating, beyond switching decor tags on and off in the playtest page to see their effect.
- The brewing mini-game and special orders.
- Voice input, English dialogue, more than one save slot, and packaging for other PCs.

## Anti-goals

Any of these would make milestone 1 a failure, even if it technically worked:

- The LLM sets numbers directly, so one clever sentence can win a neighbor over.
- Neighbors break character, forget who they are, invent facts about themselves, or turn mean.
- Bad moods spread as gossip or punish the player.
  The game stays cozy, and every friendship can recover.
- The game waits on the model to decide anything.
- Anything resembling an existing game's characters or look.

## Constraints

- Everything runs locally on this PC: Windows 10 without admin rights, an RTX 6000 Ada with 48 GB, and no cloud services.
- During development the GPU is shared with Unreal, Blender and ComfyUI, which held about 25 GB on 2026-11-25.
- The repo is public under Apache 2.0, so every persona, prompt and line must be original.
- Large files follow the fleet storage policy in `N:\2603056\AGENTS.md`.
  Model weights go under `N:\2603056\storista-cafe\checkpoints\`, written to a `.partial` folder first and published with a manifest.
- Python is managed with uv.
- Tests are end to end against the real model, with unit tests only for genuinely tricky rules.
- Branches follow the repo's flow: `feat/*` and `docs/*` branch off `develop` and merge back, and `main` only takes stable releases.

## Approaches considered

1. **Rules own the numbers, and the LLM talks and scores, in a separate local brain service (picked).**
   The brain is a small Python service that runs next to llama-server.
   The playtest page, the tests and later the Unreal game all use it over local HTTP, the same way the asset pipeline uses ComfyUI.
   You can talk to the neighbors in this milestone, long before any 3D exists, and every part runs headless for tests and tuning.
   The cost is one more process to start.
   Shipping the game to other PCs later also means bundling a Python runtime next to llama-server.
2. **LLM agents run the village.**
   Each neighbor is a full agent that plans its own day and decides whether to visit or to gossip, as in generative-agent research.
   It is rich, but it is slow and costly per in-game day, unpredictable, easy to talk into anything, and hard to test or tune.
   The game would also wait on the model for every decision.
3. **Everything inside Unreal from the start.**
   Blueprints call llama-server directly and hold the rules.
   There is only one process to ship.
   But nobody can try a neighbor until the cabin, the characters and a dialogue interface exist.
   Rules and JSON handling are clumsy in a Blueprint-only project, and nothing runs headless for tests and tuning.

Approach 1 was the recommendation, and it stands because the owner said "let's go".
It puts the owner's favorite part first, keeps the numbers fair and testable, and makes the Unreal side a thin client.

## Design

### Architecture

```
playtest page (browser) ──┐
                          ├── local HTTP, JSON ──> brain (Python) ── local HTTP ──> llama-server (Qwen 3.5)
Unreal game (milestone 2) ┘                          │
                                                     └── SQLite save
```

- **llama-server** from llama.cpp serves Qwen 3.5 on this PC.
  Output is forced to a JSON schema, and thinking is turned off for dialogue.
  The first choice is Qwen3.5-35B-A3B at Q4_K_M (22 GB), a mixture of experts with about 3B active parameters per token.
  The fallback is Qwen3.5-9B at Q4_K_M (5.7 GB), for when the GPU is crowded.
  The model is a setting, and the evaluation suite compares both.
- **The brain** is a Python service that uses only the standard library at runtime.
  It owns the persona cards, all neighbor and café state, the rules, the day and night cycle, and every call to the model.
- **The playtest page** is a static page that the brain serves.
  It is how milestone 1 is played and inspected, and it is a development tool, not the game's interface.
- **A save** is one SQLite file, including the random number generator's state, written at the end of every day.

### Persona cards

Each neighbor has one TOML file in `neighbors/`, with English keys and Traditional Chinese content.
Cards are drafted with AI help and reviewed by hand.
A card holds:

- name, pronoun, age group and role in the village;
- personality traits, and a speaking style with a few sample lines;
- interests;
- liked and disliked drinks, snacks, decor tags and weather;
- a routine: when they are free to visit;
- friendships, each with a closeness from 0 to 1;
- facts to discover (a birthday, a hobby, a dream), each with the affinity needed before they will share it;
- topics they avoid.

Cards never change during play, and everything that changes lives in the save.

### The first cast (draft)

Five neighbors are drafted here so the social graph has somewhere to flow.
The owner reviews and rewrites them, and their looks wait for milestone 2.

| Neighbor | Who they are | Likes | Friends |
| --- | --- | --- | --- |
| 小楓 (she) | The young carpenter who fixed up the cabin, and so your first customer. Quick, cheerful, talks fast. | Hot cocoa on rainy days, cinnamon rolls, wooden furniture | 阿杉 (close), 雲朵 |
| 阿杉 (he) | A shy bookbinder and 小楓's childhood friend. Few words, notices everything. | Pour-over black coffee, a quiet reading corner, poetry | 小楓 (close), 蘋婆婆 |
| 雲朵 (she) | The mail carrier who knows everyone. Chatty and warm, never unkind. | Fruit tea, iced drinks, maps and stamps | 小楓, 蘋婆婆 |
| 蘋婆婆 (she) | The retired orchard keeper and the valley's memory. Slow, kind, full of old stories. | Apple tea, knitting, old songs | 雲朵, 阿杉, 墨墨 |
| 墨墨 (he) | A painter who just moved here. Reserved and picky, hard to impress. | Matcha latte, art books, sunlight by the window | 蘋婆婆 |

At the start you know only 小楓.
The others hear about the café through friends.
小楓 can bring 阿杉 and 雲朵, they can bring 蘋婆婆, and 蘋婆婆 is the only way to 墨墨.

### A day

1. **Morning.**
   The game gives the brain the day's weather.
   The rules set each neighbor's mood and plan who visits and when (morning, afternoon or evening).
   The plan comes from each neighbor's routine, mood and affinity, and, for a neighbor who has never visited, how much they have heard about the café.
   Planning is instant and uses no model.
2. **A visit.**
   The neighbor arrives and orders.
   The rules pick the order: a drink they like that suits the weather, or now and then "surprise me".
   You serve a drink from the menu, and the rules score it.
   A liked drink helps, a disliked one costs a little, and a lucky "surprise me" helps more and may reveal a fact.
3. **Talking.**
   A visit includes a short chat of a few exchanges, which you can end at any time.
   Each of your lines, tapped or typed, goes to the model with the persona card, the neighbor's mood, relevant memories, the conversation so far, and the facts the neighbor is now willing to share.
   The model answers with one JSON object.
   It holds the neighbor's reply in their own voice, a score for how your line landed from -2 to +3 with a one-sentence reason, at most one revealed fact, and three suggestions for your next line: one warm, one curious and one playful.
   The rules apply the score with diminishing returns per neighbor per day, so the tenth compliment is worth little.
   A revealed fact goes into your notebook only if it was one of those offered to the model.
4. **Night.**
   For each neighbor you spent time with, the model condenses the day into one or two memories in the neighbor's own words, and later conversations draw on them.
   Then the rules run word of mouth.
   A neighbor who visited and is in a good mood may tell each friend about the café, with a chance that grows with their mood, their fondness for you and the friendship's closeness.
   A friend who hears about it becomes more likely to visit, and remembers who told them, so their first visit can open with "小楓說你們的肉桂捲很好吃。"
   A bad mood means fewer visits, never bad-mouthing.
   Finally the day is saved.

### The numbers

- Each neighbor has an affinity toward you from 0 to 100 and a mood for the day from 0 to 100.
  Until their first visit, they also have an interest in the café that grows through word of mouth.
- Mood starts each morning from affinity and from the weather against their preference.
  It moves during the day with drinks, talk and decor they like or dislike.
- The chances of visiting and of telling a friend rise with mood and affinity.
  Their exact shape and every constant are tuned with the simulator.
- Affinity has a soft floor, so a few bad days never close a friendship for good.
- All chance comes from one seeded random number generator stored in the save, so the rules are reproducible and tests can rely on them.

### Talking with the model

- The brain uses llama-server's OpenAI-compatible chat endpoint and forces every answer into a JSON schema.
- The brain validates and clamps the score and the facts.
  Malformed output is retried once; after that the neighbor gives a short neutral reply with no score, so a bad generation never blocks play.
- The prompt presents the player's line as something said in the café, never as instructions, and the persona tells the neighbor to stay in character.
  The evaluation suite checks that attempts to break character or to claim points fail.
- Every line must be in Traditional Chinese, and the suite measures any drift into Simplified characters.
- Target latency: the neighbor's reply within 3 seconds at the 95th percentile on this PC with the 35B model.
  The plan's first task measures it, and if the 35B misses, the 9B becomes the default.

### The brain's API

The brain listens on 127.0.0.1 only and speaks JSON over HTTP.
It can:

- report the state as the player knows it: day, weather, café, the neighbors you have met, and your notebook;
- report every number, for the playtest page's inspector and for tests;
- start a day with its weather and return the visit plan;
- serve a drink to the current visitor;
- take a line, typed or a suggestion's number, and return the reply, the score and reason, any revealed fact and new suggestions;
- end a visit;
- end the day and return the night report: new memories, word of mouth, and tomorrow's moods;
- set the café's decor tags.

The playtest page uses only this API, which keeps the API honest for the Unreal game.

### The playtest page

The page is in Traditional Chinese, and roughly:

```
┌ 第 3 天 · 雨 · 擺設：植物 ☑ 書櫃 ☐ 燈籠 ☑ ────────────────── [結束這一天] ┐
│ 今天：小楓（早上）→ 阿杉（下午）→ 雲朵（傍晚）                              │
├───────────────┬───────────────────────────────┬──────────────────────────┤
│ 鄰居           │ 小楓 · 心情 72                 │ 剛剛那句                  │
│ 小楓  ♥ 48     │ 「今天的雨好適合喝熱可可。」     │ +2 她覺得被聽見了          │
│ 阿杉  ♥ 21     │ [熱可可 ▾] [端上]              │ 筆記本：生日 3/14         │
│ 雲朵  聽說過    │ › 在練新的拉花                 │ 記憶：                    │
│ 蘋婆婆 ?       │ › 有點累，但看到你就好多了      │ 「昨天的肉桂捲很好吃。」   │
│ 墨墨  ?        │ › 你猜我今天幾點起床？          │                          │
│ [朋友關係圖]    │ [ 自己打字……           ] [說]  │                          │
└───────────────┴───────────────────────────────┴──────────────────────────┘
```

The left shows the village and the friendship graph, the middle is the visit, and the right is an inspector with the last score and reason, the notebook and the memories.

### Simulator and evaluation

- **Simulator.**
  It runs many in-game days with the rules only and a scripted player (friendly, neutral or careless) that hands out talk scores directly.
  It prints affinity, visits and word of mouth over time, so the numbers can be tuned in seconds.
  It tunes the rules and never stands in for the model in tests.
- **End-to-end tests.**
  They drive the HTTP API against the real llama-server and model.
  They cover a full day from morning to a saved night, reloading and continuing, a kind line outscoring a rude one, an attempt to claim points earning nothing, facts revealed only from those offered, and replies in Traditional Chinese.
  They need the GPU, so they run on this PC; the rule tests, typecheck and lint run anywhere.
- **Evaluation report.**
  It runs a set of scenarios per neighbor on both model sizes.
  It measures staying in character (scored against a rubric by a separate judging call), the order and spread of scores, resistance to manipulation, the rate of Simplified characters, and latency at the 50th and 95th percentiles.
  It writes an HTML report to `outputs/evals/`.

### Running it

- `tools/Start-LLM.ps1` starts llama-server with the chosen model, like `Start-ComfyUI.ps1` in the asset pipeline.
- `uv run storista-brain` starts the brain and prints the playtest page's address.
- For playing, the 35B model and Unreal fit on the GPU together.
  While ComfyUI holds its models during development, use the 9B or free ComfyUI's memory first.

### Dependencies to approve

- llama.cpp: a pinned Windows CUDA release zip, unpacked locally, with no admin rights needed.
- Qwen3.5-35B-A3B and Qwen3.5-9B at Q4_K_M: Apache 2.0 weights in community GGUF builds from Hugging Face, stored on N: under the storage policy.
- Python: nothing beyond the standard library at runtime.
  For development: pytest (already used in the asset pipeline workspace), ruff and mypy.

## Settled during review

A builder who had not seen the brainstorm read this design and asked five questions.
These are the answers, decided as sensible defaults and open to the owner's correction.

1. **What "reproducible" covers.**
   Only the rules, not the model's text, because sampled output on a GPU is not reliably identical between runs.
   The tests record the model's answers and replay them through the rules to check that the numbers match.
   Replay is a property the tests check, not a feature of the playtest page, so the save stays one file written each night.
2. **Which model "done" is measured on.**
   On the default model, chosen by the plan's first task, with ComfyUI's models unloaded, because playing never needs ComfyUI.
   The 3-second target is for the neighbor's complete reply; the suggestions may arrive a moment later.
   If the 35B misses the target, the 9B becomes the default only if it also passes the quality checks below.
   If neither passes, work stops and the choice goes back to the owner.
   The end-to-end tests run on the default model, and the evaluation report covers both.
3. **Improvising versus inventing facts.**
   Small details of the day are fine, such as when a neighbor woke up or what they had for lunch.
   Neighbors must not contradict their card or invent life facts, such as family, past, origin or anything on their list of facts to discover.
   What a neighbor says becomes part of their story only through the night memories, which record anything notable they said so later days stay consistent.
4. **How quality is checked.**
   End-to-end tests use the game's own sampling settings with a fixed seed, and assert properties with margins rather than exact text.
   For example, a kind line scores at least +1, a rude line at most 0, and an attempt to claim points at most 0.
   The evaluation report has pass marks that the plan sets: no Simplified characters, at least 90 percent of replies judged in character, and no manipulation attempt scoring above 0.
   Whether the neighbors feel alive is the owner's call, from playing the playtest page.
5. **Repetition across days.**
   Within a day, talk scores have diminishing returns per neighbor.
   Across days, a line the player already said to the same neighbor in the last seven days, after normalizing spaces and punctuation, scores 0.
   The neighbor also sees their recent memories, so they can notice when you repeat yourself.

The five persona cards are built from the drafts above.
The owner reviews them on the review page before the numbers are tuned and the evaluation is run, so that tuning is not redone.

## Left to the builder

- Exact formulas and constants, tuned with the simulator.
- Prompt wording, the JSON schema's fields, and whether the suggestions come in the same call as the reply or right after it.
- API routes and field names, and the brain's port (8000, 8188, 9876 and 4387 are taken by Unreal's MCP, ComfyUI, Blender's MCP and Lavish).
- The SQLite schema and how saves are versioned.
- How memories are picked for a prompt; the most recent ones plus a few pinned important ones is the starting point.
- How drift into Simplified characters is detected.
- Whether replies stream.
- The playtest page's exact layout, within the sketch above.

## Open for later milestones

- What the neighbors look like (people, animals or both) and how the characters are made: milestone 2.
- How the Unreal game calls the brain if the project stays Blueprint-only: milestone 2.
- Special orders and the brewing mini-game: milestone 2 or later.
- How the AI asset pipeline joins this repo: milestone 2.
- How decorating works: milestone 3.
- What there is to do in the valley: milestone 5.
- English dialogue.
