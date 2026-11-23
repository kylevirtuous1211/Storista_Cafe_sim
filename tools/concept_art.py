# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Render the Storista Cafe concept art with the local Z-Image-Turbo workflow in ComfyUI.

The ComfyUI client and the Z-Image-Turbo workflow live in the companion ai-3d-gamedev workspace.
Set AI3D_GAMEDEV to that folder; it defaults to a sibling folder named ai-3d-gamedev.
Start ComfyUI there first (pipeline/Start-ComfyUI.ps1).

    uv run tools/concept_art.py                                         # every scene at its chosen seed
    uv run tools/concept_art.py storybook_exterior storybook_interior   # only these scenes
    uv run tools/concept_art.py --seeds 101,202,303 storybook_interior  # try other seeds

Renders land in outputs/concept-art/<scene>_<seed>.png.
The JPEGs in docs/concept-art/ are these renders at their chosen seeds, saved at JPEG quality 88.
"""
import argparse
import copy
import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
WORKSPACE = pathlib.Path(os.environ.get("AI3D_GAMEDEV", REPO.parent / "ai-3d-gamedev"))
PIPELINE = WORKSPACE / "pipeline"
WORKFLOW = PIPELINE / "workflows" / "text_to_image_z_image_turbo.json"
OUTPUT_DIR = REPO / "outputs" / "concept-art"
WIDTH, HEIGHT = 1344, 768

# Each scene was rendered with seeds 101 and 202, and the better image was kept as its seed here.
SCENES = {
    # A - Pocket Diorama
    "diorama_overview": {
        "seed": 101,
        "prompt": (
            "A 3D isometric miniature diorama of a tiny cozy wooden hut coffee shop, cutaway view with the front "
            "wall and part of the roof removed so the interior is visible. Inside: a small wooden counter with a "
            "pastel mint espresso machine, a glass jar of cookies, shelves with mugs, two round tables, warm hanging "
            "light bulbs and potted plants. The hut sits on a round mossy grass base with a tiny stone path, flowers "
            "and a little tree, floating on a soft cream background. Cute chibi customers with big round heads and "
            "tiny bodies sip coffee, a chibi barista in an apron stands behind the counter. Soft pastel palette, "
            "rounded chunky toy-like shapes, smooth matte vinyl toy materials, tilt-shift shallow depth of field, "
            "soft global illumination, polished cozy game art render."
        ),
    },
    "diorama_decorate": {
        "seed": 101,
        "prompt": (
            "A 3D isometric miniature room of a cozy wooden coffee shop interior seen from above at an angle, in "
            "decorating mode: a glowing light blue placement grid covers the wooden floor, a pastel peach armchair "
            "floats slightly above the grid with a soft shadow below it as if the player is placing it. Around it: "
            "a round table, a small bookshelf, a potted monstera, a little counter with a mint espresso machine. A "
            "cute chibi barista with a big round head watches happily. Soft pastel palette, rounded chunky toy-like "
            "shapes, matte vinyl toy materials, tilt-shift depth of field, clean cream background, polished cozy "
            "game render."
        ),
    },
    # B - Storybook Cabin, the chosen look
    "storybook_exterior": {
        "seed": 101,
        "prompt": (
            "3D game screenshot of a cozy log cabin coffee shop in a forest clearing at golden hour. Hand-painted "
            "textures with soft visible brush strokes, a mossy shingle roof, smoke curling from a stone chimney, "
            "warm lantern light glowing through small square windows, a wooden porch with two little outdoor tables "
            "and potted herbs, wildflowers and ferns, tall pine trees in soft haze behind. A cute small shop owner "
            "in an apron sweeps the porch while two cute round-faced customers walk up the dirt path. Painterly "
            "storybook style, warm volumetric sunlight, soft and dreamy."
        ),
    },
    "storybook_interior": {
        "seed": 202,
        "prompt": (
            "3D game screenshot inside a cozy log cabin coffee shop on a rainy evening. Raindrops on the windows, "
            "warm amber lamps, a polished wooden counter with a copper espresso machine and a glass dome of "
            "pastries, shelves of jars and mismatched mugs, a cat sleeping on a cushion beside a small iron stove, "
            "cute round-faced customers reading at wooden tables with steaming cups. Hand-painted textures with "
            "soft brush strokes, painterly storybook style, warm cinematic lighting."
        ),
    },
    # C - Felt and Clay
    "felt_interior": {
        "seed": 202,
        "prompt": (
            "A close-up photo of a tiny handmade stop-motion animation set: a cozy coffee shop hut made of felt "
            "fabric and modeling clay, a stitched felt roof, clay mugs with visible fingerprints, button and yarn "
            "details, little wooden toy furniture. Plush toy animal customers, a small bear and a bunny, sit at a "
            "table with tiny steaming cups, and a plush fox barista stands behind the clay counter. Soft studio "
            "lighting, shallow depth of field, warm and cute, handcrafted texture everywhere."
        ),
    },
    "felt_exterior": {
        "seed": 101,
        "prompt": (
            "A handmade stop-motion miniature scene: a little wooden coffee hut with a felt roof on a patchwork "
            "fabric hill, felt trees, yarn clouds hanging on thin wires, cotton smoke rising from the chimney, clay "
            "flower pots, a tiny felt path with plush animal customers walking toward the door. Soft daylight "
            "studio lighting, shallow depth of field, cozy and charming, visible stitches and fabric texture."
        ),
    },
    # D - Toon Cafe. Thick ink outlines and a setting of its own keep it apart from existing life-sim looks.
    "toonink_interior": {
        "seed": 202,
        "prompt": (
            "Screenshot from a 3D anime-style video game with a cel-shading toon shader and thick dark ink outlines "
            "around every object: inside a small wooden hut cafe, seen in perspective from a slightly high "
            "three-quarter camera angle. A chibi barista with short auburn hair, big expressive anime eyes and a "
            "green apron pours latte art at the wooden counter, sparkles around the cup, two chibi customers in "
            "school uniforms chat excitedly on stools, cherry blossom branches visible through the window, hanging "
            "plants, stylized steam swirls. Hard two-tone shadows, bright saturated anime colors, clean and vibrant."
        ),
    },
    "toonink_exterior": {
        "seed": 202,
        "prompt": (
            "Screenshot from a 3D anime-style video game with a cel-shading toon shader and thick dark ink outlines "
            "around every object: a small wooden hut cafe beside a tiny countryside train platform under blooming "
            "cherry blossom trees in spring, petals drifting in the air, green mountains and big anime cumulus "
            "clouds in the distance, a paper lantern and a little wooden bench outside. A chibi barista with short "
            "auburn hair and a green apron waves from the cafe window while a chibi student with big anime eyes "
            "waits on the platform holding a coffee cup. Hard two-tone shadows, bright saturated anime colors, "
            "three-quarter perspective camera, clean and vibrant."
        ),
    },
}


def parse_arguments():
    parser = argparse.ArgumentParser(description="Render Storista Cafe concept art with the local ComfyUI.")
    parser.add_argument("scenes", nargs="*", metavar="scene", help=f"scenes to render (default: all): {', '.join(SCENES)}")
    parser.add_argument("--seeds", help="comma-separated seeds to render instead of each scene's chosen seed")
    arguments = parser.parse_args()
    unknown = [scene for scene in arguments.scenes if scene not in SCENES]
    if unknown:
        parser.error(f"unknown scene: {', '.join(unknown)}")
    return arguments


def main():
    arguments = parse_arguments()
    if not WORKFLOW.is_file():
        sys.exit(f"Cannot find the Z-Image-Turbo workflow at {WORKFLOW}; set AI3D_GAMEDEV to the ai-3d-gamedev folder.")
    sys.path.insert(0, str(PIPELINE))
    from comfy_client import ComfyClient, find_node

    override_seeds = [int(seed) for seed in arguments.seeds.split(",")] if arguments.seeds else None
    template = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    client = ComfyClient()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    jobs = []
    for scene in arguments.scenes or SCENES:
        for seed in override_seeds or [SCENES[scene]["seed"]]:
            graph = copy.deepcopy(template)
            find_node(graph, "Prompt")[1]["inputs"]["text"] = SCENES[scene]["prompt"]
            find_node(graph, "Sampler")[1]["inputs"]["seed"] = seed
            size = find_node(graph, "Image Size")[1]["inputs"]
            size["width"], size["height"] = WIDTH, HEIGHT
            save_id, save_node = find_node(graph, "Save Image")
            save_node["inputs"]["filename_prefix"] = f"storista-concept-art/{scene}_{seed}"
            jobs.append((f"{scene}_{seed}", save_id, client.queue(graph)))
    for name, save_id, prompt_id in jobs:
        outputs = client.wait(prompt_id)
        path = OUTPUT_DIR / f"{name}.png"
        path.write_bytes(client.download(outputs[save_id]["images"][0]))
        print("saved", path, flush=True)


if __name__ == "__main__":
    main()
