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
- **Lucky Gator Casino:** east side. The Gator Grand Hotel is behind it. Inside:
  - **Lucky Wheel:** modeled wheel with icon slices (Gator, Frog, Skull, Crown) and a bulb-lit frame. It spins and eases to a stop over 5 seconds. Bet at the four lit **bet kiosks** in front of it; each kiosk shows how many bets are on it.
  - **Swamp Slots:** 20 machines in purple, teal and red, plus 2 **Mega Slots** at the back wall. Click one: the lever pulls down and springs back, and the three reels spin several turns and stop one after another, left to right.
  - **Gator Dice:** 2 dice tables. Click to throw a pair: the dice fly in from the rim, bounce on the felt, tumble and land showing the result.
  - All casino motion uses time-synced `m-attr-anim`, so every player sees the same spin or roll, including anyone who walks up mid-roll.
  - During the Casino round, wins pay points to your team (5 second cooldown per player). Outside the round everything is free play.
- **Gator Pit arena:** west side, with the gold throne in the middle.
- **Bayou Heights:** downtown towers and Bayou PD to the north.
- **Neon Row:** bars and shops to the south, with stilt shacks behind them.
- **Outer districts (new):** a second ring of blocks around downtown, about 430 m across in total.
  - **Cannery Row (north):** warehouses and the Bayou Cannery with its smokestacks.
  - **Bayou Village (south):** stilt shacks and the Swamp Fair.
- **Swamp Fair** (south of the city, through the striped gate). Every ride carries players on hidden floors that move with it:
  - **Bayou Eye:** a 14 m Ferris wheel with 12 lit gondolas that stay level. It never stops (one loop every 2 minutes): climb the platform stairs and hop into a gondola as it passes the bottom. Each gondola has solid MML surfaces that turn with it (a wooden floor, waist-high walls and gold rails), so avatars stand on real primitives rather than the model.
  - **Gator-Go-Round:** a carousel with 16 bobbing gators and frogs under a striped canopy. It turns slowly all the time; step on from the boarding ring.
  - **Gator Drop:** a 32 m tower topped with a giant gator head. Hop on the ring while it says BOARDING; it climbs 26 m, hangs, then drops. The sign counts down to the next drop.
  - **Whack-a-Gator:** click the counter to play. Gators pop up for 20 seconds; bop as many as you can. The booth shows the high score.
  - **Test Your Bite:** a high striker. Click SWING! when the needle is far right; ring the bell for GATOR!
  - Food stands (Funnel Cakes, Boudin Balls, Snowballs, Gator on a Stick), a sawdust promenade and string lights.
  - **Voodoo Quarter (east):** colorful balcony buildings and the KGTR radio tower.
  - **Gator Flats (west):** shacks, trailers and the Gator Junk yard.
  - Small marsh parks with ponds and cypress trees are scattered through the blocks.
- **Team hideouts:** one in each outer corner, each with a buggy parked beside it. All four are the same distance from the bank vault (about 175 m), so the Bank Job is fair and buggies really help.
- **The edge of town:** the city ends at a stone seawall with a boardwalk quay. There is no open water any more; every boat is docked in its own small slip against the wall, and short marina piers stick out on the east and west sides.

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
| **Bank Job** | 4 min | Grab a money bag at the vault and deliver it to your own hideout's DROP LOOT board for +1. While you carry it, a money bag rides on your back so everyone can see who has the loot. A bag's dye pack explodes after 75 s (red puff). |
| **Gator Pit** | 3 min | The team with the most players on the throne scores +1 per second. A tie scores nothing. The last 30 s are worth double. |
| **Lucky Wheel** | 6 spins | Bet on a board during the 20 s window. GATOR, FROG and SKULL pay +2; CROWN (1 slot in 10) pays +6. |
| **Turf War** | 4 min | Walk up to any house, open the door, go inside and click **CLAIM THIS HOUSE** on the back wall. Every 10 s, each house you own scores +1. A house locks for 8 s after each claim, and a player can claim once every 3 s. Doors swing open when clicked and close on their own after 12 s. |

Every point counts toward **series points**, which add up across all games until you press **Reset series points**. Use them for the weekly leaderboard. When a game's timer ends, the big screen shows the winner and returns to intermission.

## Vehicles

There are **12 drivable trucks**. The **36 boats** (3 motor yachts, 2 sailboats, 8 airboats, 7 shrimp boats and 16 skiffs) are parked: each one is moored in a slip against the seawall and bobs gently.

- **Trucks** are modeled pickups (`pickup-red`, `-blue`, `-gold`, `-green`, CC0, made for this build). They have a rounded body, wheel arches with fender flares, a chrome grille, bumpers and bull bar, glowing headlights and taillights, off-road tires with chrome rims, running boards, a roof light bar and a wooden bed floor. They sit on the road.
- **Drive:** click any vehicle, or its "CLICK TO DRIVE" sign, to take the wheel. A console appears at waist height at the front of the riding area, tilted up toward you like a dashboard, so it never blocks your view ahead. It has **< LEFT, GO, RIGHT > / BACK, STOP, EXIT**. Whichever of GO, BACK or STOP is active lights up, and the top line shows the speed. Only the driver sees the console. The "click to drive" signs hide while someone is driving, so the riders' view stays clear.
- **Slow and smooth:** every vehicle starts very slowly, builds up gently and stays at a relaxed pace. Trucks reach about 22 km/h and airboats about 25. Skiffs and yachts are slower still, and sailboats are the slowest. STOP slows the vehicle gradually, a parked vehicle coasts to a halt, and turns ease round to the new heading.
- **Ride:** every vehicle has an invisible MML floor matched to its deck, plus low invisible rails, so riders stay on while it moves. Trucks carry riders in the bed, with two metal steps at the tailgate to climb in. Yachts, sailboats and shrimp boats have boarding steps on both sides; riders stand on the back deck.
- **Trucks** stop when they hit a building.
- **Where they are:** 4 trucks at the plaza, one at each hideout and four on the middle ring road. Boats: a yacht and a sailboat at each marina pier, four airboats and four skiffs along the east and west walls, shrimp boats by the cannery (north) and along the south wall, one more yacht by the fair, and skiffs along the north and south walls.
- Vehicles nobody drives for 2 minutes are released. **Reset all buggies** in the controller puts every truck back where it started.

## Kenney models (CC0)

The world is dressed with free CC0 models by [Kenney](https://kenney.nl), taken from his official starter kits on GitHub:

- **Trucks:** pickup trucks replace the buggies. Ride in the bed; the dashboard sits at the back of the cab.
- **Voodoo Quarter and Gator Flats:** townhouses.
- **Cannery Row:** garages and warehouses.
- **Plaza:** two fountains.
- **Bank Job:** spinning gold coins at the vault.
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
- **Casino:** patterned red carpet with swamp flowers, wood art-deco wall panels, coffered gold ceiling, chandeliers, gold columns, felt card tables, polished wood, slot machine screens and a lit bulb border.
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
| Swamp Fair | The name panel on the modeled entrance arch |
| Check-in sign | A wooden board hanging from chains |

**Lighter for big groups:** the world now sends about half as many elements when players join (about 1,560 instead of 3,120).

**When it turns on:** with `BAKED: true` and the asset pack hosted, *and* all the other add-ons on (`KENNEY`, `NATURE`, `MEDIEVAL`, `DOWNTOWN`, `STREETS`) at normal detail. In any other setup the world falls back to the primitive version, so it always works. Moving and clickable pieces (vehicles, airboats, the Ferris wheel, the vault, check-in stands, bet boards and turf walls) are still live MML elements, because they have to move or respond to clicks.

## Boats, a smaller swamp and new clouds (earlier update; the swamp has since been removed)

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

## Enterable houses (update)

- **Every house can be entered and claimed:** 101 in all. That's every block-built house, shop, bar and shack, plus every Old Town (medieval) house. Each has a working wooden door, a room inside with a wooden floor, ceiling and lamp, and a **CLAIM THIS HOUSE** button on the back wall. The sign over the door and the door itself turn your crew's color when you own it.
- **On the ground:** the stilt shacks now sit on the ground, and their porches and stairs are gone. Every house's floor is level with the street.
- **Old Town houses** were rebuilt (`med-*-v3`) with an open doorway, a wooden floor and a ceiling, so you can walk inside.
- The Kenney townhouses and garages and the downtown brick buildings are scenery and can't be entered.

## Optional add-ons (top of the world file)

- `CASTLE_BASE`: the folder URL holding your princess castle GLBs. The castle then appears on Queen's Isle, out in the swamp north of the city.
- `FRAMES`: embed other MML documents, such as the Spire, with `m-frame` at a position you choose.
- `MODELS`: swap in CC0 GLBs for the buggy, airboat or gators.
- `DETAIL: "low"`: cuts trees, reeds, lily pads, street lamps and outer-district buildings for weaker devices.

## Every door faces its street (update)

- All 142 buildings with a door (101 houses you can claim in Turf War, 6 towers and 35 model buildings) were checked by tracing a 1.8 m wide path straight out of each door: every one now reaches a street or the plaza without passing between other buildings.
- Turned to face their street: Gator Grand Hotel (it faced the back of the casino), Pelican Motel (also faced the casino), Gator Farm, Live Bait and the shack next to the farm, the two corner towers and two houses north of downtown, and the eight stilt houses behind Neon Row.
- The cannery's loading dock was split in two so its front door opens straight onto the street.
- `tools/doorcheck.py` is the check (it reads a door dump from a debug run of the world).

## A smaller build: no outside water (update)

- The round swamp is gone. The world now ends at the city's stone seawall (430 m square), so the whole build is much smaller.
- The two 102 m airboat piers are now 16 m marina piers. Every boat is docked in its own stone-edged slip of water against the wall and is parked scenery (trucks are still drivable).
- The swamp trees, reeds, rocks, lily pads and swimming gators that stood in the water were removed; a few gators now bask on the quay by the boats, and the Gator Farm gators are still there. Clouds stay over the city.
- `tools/docktest.mjs` checks that all 36 boats are docked at the wall and that nothing is left out past the slips.

## Bank and signs (update)

- **Bayou Savings & Trust** is a modeled neoclassical bank: rusticated stone, a four-column front with a pediment and gold medallion, arched windows, a copper dome with a lantern, ATMs and bronze lamps out front. Inside: a checkered marble hall, teller counters with brass grilles, chandeliers and a velvet-rope queue.
- **The vault** is a riveted steel vault with two huge round doors swung open and shelves of money bags and gold bars. During the Bank Job, piles of money bags surround it.
- **Carried bags** use an MML position probe (only while the Bank Job runs) to put a money bag on each carrier's back.
- **Signs** are broader and each business has its own GTA-style look: script neon for bars and the motel, bold billboards for the pawn shop and fast food, a police badge sign, stencil hideout signs and green highway-exit signs for the districts. Fonts: Anton, Bungee, Bebas Neue, Pacifico, Lobster, Monoton, Black Ops One, Alfa Slab One, Racing Sans One, Permanent Marker, Oswald (SIL Open Font License).

## Gator Junk redressed (update)

The junkyard is now a real wrecking yard, built as one model (`gator-junk`, CC0):

- Rusted wrecks in six faded colors with cracked glass, open hoods, missing doors and missing wheels propped on cinder blocks. They're stacked two and three high along the fences, with one on its roof and one tipped up on a tire pile.
- A crawler crane lifting a wreck on its electromagnet, and a car crusher with a flattened car and a pyramid of crushed bales beside it.
- Tire towers, oil drums, a scrap heap bristling with bars and panels, engine blocks on a pallet, and the office trailer up on blocks.
- A burn barrel with a glowing fire, two floodlights, a dirt yard with oil stains, and fence posts with barbed wire. The gates swing open onto the street.

Players can climb on the wrecks.

## Placed in front of you (update)

When you place the build, you now stand just **outside** it, on solid ground at the foot of the east dock, with the whole city straight ahead of you. A boardwalk with two lamps runs from your feet onto the marina pier and leads straight to the Visitor Center. The Visitor Center was turned around to face the dock, so its big screen, check-in stands and the "WELCOME TO SWAMP CITY" arch greet you as you walk in.

- `SPAWN: "front"` (the default) is this placement. `"edge"` stands you on the Visitor Center plaza instead, and `"center"` is the old bank-centred placement.
- `TURN: 0` turns the whole build by 90, 180 or 270 degrees if Otherside puts it beside or behind you instead of in front.

## Hideout beacons always on (update)

Every hideout now has a glowing beam in its crew's color shooting straight up out of the roof, about 60 m tall and fading out toward the top. It stays on all the time, not just during the Bank Job, so each crew can find home from anywhere in the city. New models: `beam-gator`, `beam-heron`, `beam-frog`, `beam-snake` (CC0).

## Bayou Run removed (update)

The race game and its 15 checkpoint gates are gone. Four games remain: Bank Job, Gator Pit, Lucky Wheel and Turf War. The controller no longer has a Bayou Run button, so use the new controller file.

## Renames (update)

From the names sheet: the blue crew HERONS is now **MUNYONS** (hideout, stand, screen and controller; their mascot is still the heron), Lucky Gator Casino is now **TOKEN GATOR CASINO**, Bayou Savings & Trust is now **YUPPIE APE SAVINGS & TRUST**, and the JAZZ shop signs now read **CURTIS**. `city-c` was re-baked for the new signs.

## Visitor Center, spawn at the edge, crew mascots and lit hideouts (update)

- **Visitor Center on the east edge.** Everyone arrives here and checks in. It has a stucco hall with a clock tower and copper dome, a porch with a neon edge, and the big intermission screen (moved off the bank). The four crew check-in stands sit in front, each with its mascot turning on top. A "WELCOME TO SWAMP CITY" arch leads out to the street, and four trucks are parked on the plaza. The KGTR radio mast that stood on this block is gone.
- **You spawn at the edge, not the middle.** The world is shifted so the Visitor Center plaza (the gold-ringed pad) is the document origin. Wherever you place the build in Otherside, that spot is the Visitor Center, and the city stretches about 380 m east-to-west from it. Set `SPAWN: "center"` at the top of the file to go back to the old bank-centred placement.
- **The old check-in spot by the bank** now has a green freeway sign: "TEAM CHECK-IN - VISITOR CENTER - EAST EDGE".
- **Crew mascots over every checked-in player.** GATORS get a little gator, HERONS a heron, BULLFROGS a bullfrog and COTTONMOUTHS a coiled purple snake. Each glows in its crew color, turns slowly and bobs over the player's head. Everyone can see them. They swap if you switch crews and disappear when you leave. One shared position probe (about 3 updates a second; tiny movements are skipped) drives both the mascots and the Bank Job money bags.
- **Hideouts lit in their crew's color.** Each hideout has a light in its crew color over the forecourt, plus neon trim on the roofline, corners and shutter, two floodlight heads and a colored glow on the ground.
- New models (CC0, made for Swamp City): `team-gator`, `team-heron`, `team-frog`, `team-snake`. `city-a`, `city-b` and `city-c` were re-baked.

## Audit fixes (18 Nov 2026)

An outside audit found two real problems; both are fixed.

- **Doc now starts on standard MML servers.** The packed loader used `Blob.stream()` and `DecompressionStream`, which the standard Node/JSDOM MML runners don't have. It still tries those first and now falls back to a small built-in gzip decoder. The packed doc passes the full game, boat and casino tests on a standard runner.
- **Every model now has UVs.** 51 models had parts with no texture coordinates (`TEXCOORD_0`), which some viewers, including Otherside, may not render. `city-b.glb` also had broken (NaN) UVs on its lamp globes. All 99 models now pass the Khronos glTF validator with 0 errors and 0 warnings, and they look identical.
- **Tools** (in `tools/`): `uvscan.mjs` lists models with missing or broken UVs; `uvfix.mjs in.glb out.glb` adds them without changing anything else. Run both on any new model before uploading.

## Known limits

- **Riding vehicles:** whether players get carried on a moving buggy or airboat depends on the client. Test this in your viewer; if riders slide off, players can still drive the buggy while running beside it.
- **Steering:** buggies turn in 22.5° steps, because MML has no held-key controls.
- **Hosting models on GitHub:** raw.githubusercontent.com can rate-limit when a big crowd joins at once. For a live event, upload the models to the MML editor (mmlstorage) and use `ASSET_URLS`, like the live build does.
- **Water level:** the water sits at y -0.42. Place the world on flat ground, or terrain can poke through the water.
- **Size:** with the baked city, the world has about 1,560 elements on join, plus about 8 MB of baked models (cached after the first load). Desktop is fine; on phones, try `DETAIL: "low"` first.
