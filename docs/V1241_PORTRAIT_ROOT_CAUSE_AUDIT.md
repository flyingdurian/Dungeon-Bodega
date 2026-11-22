# Portrait runtime audit — V1.2.4 baseline

Source: V1.2.4 packaged Godot project; independent asset inventory, not a live Godot screenshot.

| Character | Production states / 12 | Native-size RGBA / 12 | F2 candidate files | Approved | Runtime action |
|---|---:|---:|---:|---|---|
| liu_xue | 5/12 | 0/12 | 0 | No | Expression files when present |
| elara_veyne | 8/12 | 0/12 | 0 | No | Expression files when present |
| master_chen | 1/12 | 0/12 | 4 | No | Forced neutral |
| tarek_ashwood | 8/12 | 0/12 | 0 | No | Forced neutral |
| felix_rowe | 8/12 | 0/12 | 0 | No | Forced neutral |
| safiya | 1/12 | 0/12 | 0 | No | Forced neutral |
| rin_kaede | 1/12 | 0/12 | 0 | No | Forced neutral |
| yuna_seo | 8/12 | 0/12 | 0 | No | Forced neutral |
| mara_copperwell | 8/12 | 1/12 | 0 | No | Forced neutral |

## Root causes
1. In `Main.gd::_show_portrait`, all seven rejected IDs go through an approval check that replaces any requested expressive texture with `vn_<id>_neutral.png`.
2. The rejection manifest marks all seven `approved=false`; the game therefore stays neutral regardless of what dialogue emotion is reported.
3. Master Chen, Safiya and Rin lack production expression sets; Tarek, Felix, Yuna and Mara have mostly small expression bust crops (not usable as full hero portraits).
4. Rin neutral has visible embedded scene content even though outer PNG edges are transparent; transparency tests alone cannot catch that.
5. Benchmark figures are not themselves 12-state complete: Liu Xue has five full-size expressive paintings, Elara eight.
6. `selected_expression` formerly recorded the requested emotion even while the renderer displayed neutral, obscuring diagnosis.

## Correct production remedy
Author 12 distinct, transparent, identity-locked portrait masters per rejected visitor at 1024×1536 or higher; align character focal point and crop across every state. Review all 12 per visitor in F2, then use the project art validator and the owner’s visual approval before enabling runtime production art.
Do not promote sheet crops, upscale existing reaction busts, or mark approval without review. New diagnostics now show requested versus actually displayed state in F4.

## Release status
Portrait art: **BLOCKED**; code instrumentation: implemented, needs native Godot runtime verification.

