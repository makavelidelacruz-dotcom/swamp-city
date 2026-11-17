# Chaos Trials: Swamp City

A Grand Theft Auto style MML world for 4 teams and 50+ players. It uses the same setup as Grand Theft Dino: players check in at team stands, and the host runs one game at a time from the controller page.

## Files

| File | What it is |
|---|---|
| `chaos-trials-swamp-city.html` | The world. Paste it into the MML editor (or any MML server) and run it. |
| `chaos-trials-controller.html` | The host controller. Open it in a browser on your own computer. |

## Before the event

1. **Change the host code.** Open the world file and edit `HOST_KEY` near the top. Use a long random string, and keep the file private.
2. **Run the world** in the MML editor and copy its `wss://` address.
3. **Open the controller**, paste the address and your host code, and press Connect. The pill turns green when it finds the game.
4. **Do a test run** with a few people: check in, drive a buggy, and run one round of each game.

## The city

- **Plaza (spawn):** Bayou Savings bank with the big screen on its front, the 4 team check-in stands, and 4 buggies.
- **Bank vault:** inside the bank, with doors on the north and south sides.
- **Lucky Gator Casino:** east side, with the Lucky Wheel inside. The Gator Grand Hotel is behind it.
- **Gator Pit arena:** west side, with the gold throne in the middle.
- **Bayou Heights:** downtown towers and Bayou PD to the north.
- **Neon Row:** bars and shops to the south, with stilt shacks behind them.
- **Outer districts (new):** a second ring of blocks around downtown, about 430 m across in total.
  - **Cannery Row (north):** warehouses and the Bayou Cannery with its smokestacks.
  - **Bayou Village (south):** stilt shacks and the Swamp Fair with a turning Ferris wheel.
  - **Voodoo Quarter (east):** colorful balcony buildings and the KGTR radio tower.
  - **Gator Flats (west):** shacks, trailers and the Gator Junk yard.
  - Small marsh parks with ponds and cypress trees are scattered through the blocks.
- **Team hideouts:** one in each outer corner, each with a buggy parked beside it. All four are the same distance from the bank vault (about 175 m), so the Bank Job is fair and buggies really help.
- **The swamp:** players can wade anywhere around the island. Four airboats circle the city, and players board them from the long east and west piers.

## Teams

| Team | Color | Hideout |
|---|---|---|
| GATORS | Green | North-east |
| HERONS | Blue | South-west |
| BULLFROGS | Gold | South-east |
| COTTONMOUTHS | Purple | North-west |

Players click their team's stand and type a name. Clicking another stand switches teams.

## Games

| Game | Length | How it scores |
|---|---|---|
| **Bank Job** | 4 min | Grab a bag at the vault and deliver it to your own hideout's DROP LOOT board for +1. A bag explodes after 75 s. |
| **Bayou Run** | 5 min | Hit 15 checkpoints in order, on foot or driving. 1st, 2nd and 3rd score 10, 8 and 6; every other finisher scores 3. Each player only sees a beam over their own next gate. |
| **Gator Pit** | 3 min | The team with the most players on the throne scores +1 per second. A tie scores nothing. The last 30 s are worth double. |
| **Lucky Wheel** | 6 spins | Bet on a board during the 20 s window. GATOR, FROG and SKULL pay +2; CROWN (1 slot in 10) pays +6. |
| **Turf War** | 4 min | 20 walls across the city. Click a wall to tag it in your color. Every 5 s, each wall you own scores +1. A wall locks for 8 s after each tag. |

Every point counts toward **series points**, which add up across all games until you press **Reset series points**. Use them for the weekly leaderboard. When a game's timer ends, the big screen shows the winner and returns to intermission.

## Vehicles (every truck and boat is drivable)

There are **47 drivable vehicles**: 12 trucks and 35 boats (3 motor yachts, 2 sailboats, 8 airboats, 7 shrimp boats and 15 skiffs).

- **Drive:** click any vehicle, or its "CLICK TO DRIVE" sign, to take the wheel. Only you see its control panel, which floats in front of the riders: **LEFT, GAS, RIGHT / REVERSE, BRAKE, EXIT**. The panel's top line shows FORWARD, REVERSE or STOPPED. Click EXIT to park it, and anyone can then take it.
- **Ride:** every vehicle has an invisible MML floor matched to its deck, plus low invisible rails, so riders stay on while it moves. Trucks carry riders in the bed, with two metal steps at the tailgate to climb in. Yachts, sailboats and shrimp boats have boarding steps on both sides; riders stand on the back deck. Airboats and skiffs carry riders on the open deck.
- **Trucks** sit on the road, top out at 14 m/s and turn in 22.5° steps. They stop when they hit a building, and they're amphibious, so they can drive out into the swamp.
- **Boats** stay in open water, so they can't drive onto the island or through the piers, and they stop at the edge of the swamp. Airboats are the fastest (15 m/s); yachts and skiffs do 10, shrimp boats 8 and sailboats 7. Yachts, sailboats and shrimp boats turn in 15° steps.
- **Where they are:** 4 trucks at the plaza, one at each hideout and four on the middle ring road. Each pier has a yacht, a sailboat, four airboats and three skiffs, with one more yacht on the west pier. Shrimp boats are moored off the north and south shores and out in the open water, and the other skiffs sit along the shoreline.
- Vehicles nobody drives for 2 minutes are released. **Reset all buggies** in the controller puts every truck and boat back where it started.

## Kenney models (CC0)

The world is dressed with free CC0 models by [Kenney](https://kenney.nl), taken from his official starter kits on GitHub:

- **Trucks:** pickup trucks replace the buggies. Ride in the bed; the dashboard sits at the back of the cab.
- **Voodoo Quarter and Gator Flats:** townhouses.
- **Cannery Row:** garages and warehouses.
- **Plaza:** two fountains.
- **Bank Job:** spinning gold coins at the vault.
- **Swamp Fair:** fair tents.
- **Neon Row:** parked motorcycles.
- **Sky:** drifting clouds.

**Where they load from**

| Setting | What happens |
|---|---|
| Default | Models load straight from Kenney's public GitHub repos, pinned to a fixed version. Nothing to upload. |
| `ASSET_HOST` | Upload the `swamp-city-assets` folder (54 GLBs, about 9 MB, textures built in) to your own host and put the folder URL here. |
| `ASSET_URLS` | Paste one URL per file, for example `"truck-red": "https://mmlstorage.com/..."`, if your host gives each file its own link. |
| `KENNEY: false` | Turns the models off and goes back to the all-primitive look. |

For a live event, hosting the pack yourself is safer than relying on GitHub staying up.

## Swamp nature models (from your AllModels.blend)

The file is Quaternius's "Ultimate Stylized Nature" pack (CC0). I converted 24 of its models:

- **10 dead trees:** dark snags and pale ghost trees, standing in the swamp shallows and replacing some of the cypresses.
- **3 leafy trees:** these replace the primitive trees in the plaza, parks and city blocks.
- **Bushes and flowering plants:** around the plaza, the pond, the hideouts and the outer blocks.
- **Tall grass clumps:** along the shoreline, in place of the old reed sticks.
- **5 rocks:** on the shoreline, in the junk yard and in the outer blocks.

Most of the textures in the .blend weren't packed, so the dead trees and rocks use flat swampy colors and the leafy trees borrow the pack's bush-leaf texture. The pine, palm and birch trees were left out because they don't fit a swamp, and the maple was too heavy for what it adds.

**These only show up once you host the asset pack.** Unlike the Kenney models, they aren't online anywhere yet. Until you set `ASSET_HOST` (or every nature entry in `ASSET_URLS`), the world keeps its primitive trees, so it always works.

**Easiest hosting:** put the `swamp-city-assets` folder in a public GitHub repo, like your Spire, then set:

```
ASSET_HOST: "https://raw.githubusercontent.com/YOUR-NAME/YOUR-REPO/main/swamp-city-assets/",
```

That one setting loads the Kenney, nature, Old Town and Uptown models from your copy.

## Old Town models (from your Medieval Village MegaKit)

The kit is CC0 (Quaternius's free Standard version). It's a set of modular pieces, so I assembled four houses from its walls, roofs, balconies, doors, chimneys and vines, and saved each one as a single light model:

| Model | What it is |
|---|---|
| `med-house` | 2-floor half-timbered house, brick ground floor, balcony, chimney, vines |
| `med-townhouse` | Narrow 3-floor townhouse with balcony |
| `med-hall` | Long brick hall with a wagon out front |
| `med-cottage` | Small 1-floor cottage |

Props: wagon, crate, wooden fence and wrought-iron railing.

**Where they appear**
- **Old Town (west, formerly Gator Flats):** about two-thirds of the buildings are now these houses.
- **Bayou Village:** a few cottages mixed in with the stilt shacks.
- **Plaza pond:** wrought-iron railings on both sides, New Orleans style.
- **Wagons and crates:** at the Cannery docks, the Swamp Fair, Gator Junk and the Gator Farm (which also gets a wooden fence).

Each house is about 0.6 MB, with textures shrunk to 512 px WebP. Like the nature models, they turn on once the asset pack is hosted (`MEDIEVAL: true` plus `ASSET_HOST`); otherwise the world keeps its other buildings.

## Uptown models (from your Downtown City MegaKit)

The kit is CC0 (Quaternius's free Standard version). It came with three finished brick buildings, which I simplified to cut 25 to 42% of their triangles and compressed to 0.7 to 1.2 MB each:

| Model | Size |
|---|---|
| `dt-large` | 9-story office block, 21 by 17 m, 28 m tall |
| `dt-medium` | Ornate brick hotel, 15 by 13 m, 25 m tall |
| `dt-small` | Brick walk-up, 12 by 15 m, 17 m tall |

Props: bollards, planters, rooftop AC units and manhole covers.

**Where they appear**
- **Uptown (north, formerly Cannery Row):** almost half the buildings are now these brick blocks, some with planters out front. The Bayou Cannery itself stays.
- **Voodoo Quarter:** a few brick walk-ups mixed in with the townhouses.
- **Tower rooftops:** AC units.
- **Bollards:** along the casino front and the plaza's south edge.
- **Neon Row:** planters out front.
- **Streets:** about 40 manhole covers.

I removed the kit's built-in "wear mask" colors, because MML viewers showed them as red smears. Like the other add-ons, these turn on once the pack is hosted (`DOWNTOWN: true` plus `ASSET_HOST`).

## Streets, grass and fixes (update)

- **Streets:** textured asphalt with a double yellow center line and white edge lines, concrete sidewalks with curbs on both sides, and zebra crosswalks at every intersection. Six small models (`road-seg-34`, `road-seg-84`, `road-seg-4`, `road-cross`, `ground-grass`, `plaza-pavers`) replace the old flat strips.
- **Grass:** a textured lawn covers the whole island, with about 150 extra grass clumps in the lots.
- **Plaza:** paved with warm stone bricks.
- **Fixed:** the medieval houses' side and back walls now face outward. Before, they were turned sideways or inward.
- **Fixed:** every model now uses standard JPEG/PNG textures and no compression extensions, so it loads in Otherside and other MML viewers. The earlier WebP version showed up white there.

## Detailed textures and real signs (update)

Every static building block in the city is now **baked into five textured models** (`city-a` to `city-e`), so the blocky flat-colored boxes are gone:

- **Buildings:** plaster, clapboard siding, red brick, stucco and concrete skins, with corner pilasters, stone plinths, floor bands and cornices. Windows have frames, mullions, sills, curtains and a warm lit interior. Shacks get wooden shake roofs; other houses get clay tile roofs. Doors are paneled wood; towers have glass curtain walls and glass entry doors.
- **The bank:** cut limestone walls, fluted columns, a marble entry step, a carved stone cornice, an aged copper dome and gold vault doors.
- **Casino:** patterned red carpet, art-deco wall panels, gold columns, felt card tables, polished wood, slot machine screens and a lit bulb border.
- **Gator Pit:** a log palisade, wooden bleachers, sand floor and steel floodlight poles.
- **Hideouts:** corrugated metal with ribbed roll-up shutters in the team color.
- **Swamp:** muddy banks, stone embankments, rippled water, lily pads, plank boardwalks and bark-textured pilings.

**Signs now belong to the world instead of floating:**

| Sign | Looks like |
|---|---|
| Rooftop signs | Neon letter boards on steel legs with braces and three gooseneck lamps |
| Bait shop, gumbo hut, pawn shop, farm, junk yard, cannery | Hand-painted wooden boards |
| Tower and hideout signs | Framed boards bolted to the wall |
| Casino and big-screen header | Marquee boxes ringed with lit bulbs |
| Bank | Gold letters carved into a limestone panel with gold trim |
| Gator Pit, district and airboat signs | Boards on two iron posts |
| Swamp Fair | An entrance arch with striped pillars and gold balls |
| Check-in sign | A wooden board hanging from chains |

**Lighter for big groups:** the world now sends about half as many elements when players join (about 1,560 instead of 3,120).

**When it turns on:** with `BAKED: true` and the asset pack hosted, *and* all the other add-ons on (`KENNEY`, `NATURE`, `MEDIEVAL`, `DOWNTOWN`, `STREETS`) at normal detail. In any other setup the world falls back to the primitive version, so it always works. Moving and clickable pieces (vehicles, airboats, the Ferris wheel, the vault, check-in stands, bet boards and turf walls) are still live MML elements, because they have to move or respond to clicks.

## Boats, a smaller swamp and new clouds (update)

- **Smaller, round swamp:** the swamp is now a circle 720 m across (radius 360 m), which cuts the open water by about 70% from the 980 m square. The city, buildings, streets and piers are the same size, and the airboat loop, work-boat loop and outer gators all sit inside the new shoreline.
- **Original boat models** (modeled in Blender for this build, CC0):

| Model | What it is | Where |
|---|---|---|
| `yacht-1`, `yacht-2` | 18 m motor yacht: teak decks, tinted saloon windows, flybridge with hardtop, radar arch, chrome rails, swim platform, fenders | Tied up along the east and west piers |
| `sailboat` | 14 m sailing yacht with mast, rigging, furled sails and wheel | One at each pier |
| `airboat-1` to `airboat-4` | Airboat with raised driver's seat, V8 engine, prop cage, twin rudders and a flag, in four colors | **8** on the Bayou Loop (up from 4), still rideable from the piers |
| `airboat-prop` | The wooden fan, which spins on every airboat | |
| `shrimpboat-1`, `shrimpboat-2` | 14 m bayou shrimp trawler with wheelhouse, outrigger booms and hanging nets | Moored off the north and south shores, and cruising an outer loop |
| `skiff-1`, `skiff-2` | Aluminum jon boat with outboard motor | Beside the piers, along the shoreline and on the outer loop |
| `gator`, `gator-bronze` | 4 m American alligator: armored back scutes, pebbly flanks, cream belly plates, yellow eyes with slit pupils, teeth along both jaws, back and tail crests, bent legs with clawed toes. The bronze version is for the statues | 12 swimming around the city, 12 basking in the shallows, 4 at the Gator Farm, and the bronze statues in the plaza fountain and the Gator Pit |


- **Clouds:** three new puffy cloud models (`cloud-1` to `cloud-3`) with a sunlit top fading to a soft blue-grey underside, plus 10 big high clouds further out.
- Turn these off with `BOATS: false`; the world then goes back to the old airboats and clouds.

## Optional add-ons (top of the world file)

- `CASTLE_BASE`: the folder URL holding your princess castle GLBs. The castle then appears on Queen's Isle, out in the swamp north of the city.
- `FRAMES`: embed other MML documents, such as the Spire, with `m-frame` at a position you choose.
- `MODELS`: swap in CC0 GLBs for the buggy, airboat or gators.
- `DETAIL: "low"`: cuts trees, reeds, lily pads, street lamps and outer-district buildings for weaker devices.

## Known limits

- **Riding vehicles:** whether players get carried on a moving buggy or airboat depends on the client. Test this in your viewer; if riders slide off, players can still drive the buggy while running beside it.
- **Driving through checkpoints:** in Bayou Run, a driver gets credit for a checkpoint by driving through it, but passengers do not.
- **Steering:** buggies turn in 22.5° steps, because MML has no held-key controls.
- **Size:** with the baked city, the world has about 1,560 elements on join, plus about 8 MB of baked models (cached after the first load). Desktop is fine; on phones, try `DETAIL: "low"` first.
