# Storista Café

A cozy idle game about running a little coffee shop: decorate your café, meet the neighbors, explore the neighborhood.

![Concept art: a hand-painted log cabin coffee shop in a forest clearing at golden hour](docs/concept-art/storybook_exterior.jpg)

**Status:** designing.
Nothing is built yet.
The decisions, proposals and open questions so far are in [docs/brainstorm-notes.md](docs/brainstorm-notes.md).

## The game so far

- Full 3D in a hand-painted storybook look: a log cabin café in the woods, with weather and time of day.
- You start from an empty shop and decorate it your own way.
- Neighbors have fixed personas, likes and friendships, and a local LLM gives them their voices.
  Their mood decides whether they visit and whether they tell their friends about you.
- Everyday orders are quick, and special orders are brewed by hand.

## How it is being made

The plan is to build on a local, no-admin AI pipeline proven in an earlier demo: Unreal Engine 5.8, Blender 5.1 and ComfyUI (Z-Image-Turbo for images, TRELLIS.2 and Pixal3D for 3D props), driven by Claude Code through MCP.
That pipeline lives in a separate local workspace for now, and the design doc will settle how it joins this repo.

## Layout

- `docs/brainstorm-notes.md` - decisions, proposals and open questions so far.
- `docs/concept-art/` - concept art for the four looks that were compared.
- `tools/concept_art.py` - re-renders that concept art with the local ComfyUI (`uv run tools/concept_art.py`).

## License

Apache License 2.0; see [LICENSE](LICENSE).
