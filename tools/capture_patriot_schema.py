#!/usr/bin/env python3
"""Capture the exact reviewed PatriotFix 0.2.2 source; refuse all source drift.

This is an explicit version-specific byte allowlist, not general C++ support.
Authenticates the local Git HEAD separately from the reviewed source hashes.
Hidden PW fields are included because Config Tool saves every control.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

try:
    from tools.capture_settings_schema import braced, split_items, without_comments
except ModuleNotFoundError:
    from capture_settings_schema import braced, split_items, without_comments

TREE = "c8e76fe99c66a5cee6b112fbd80cbd8eb7b522de"
REVIEWED = {'ConfigTool/helper.cpp': '582783fdd792b092424dd12393daa3d17da36e31686b4dab415fcc72b3276cc8',
 'ConfigTool/helper.hpp': '987bbc63bbbe6fb09e6a3967db7a58b19300ee02fb4e07247369b23b258db5e9',
 'ConfigTool/main.cpp': '8ea2c96aebccb703847cf4af5602f79310c02e646a780c89bdb2ce3ceda2e7e7',
 'ConfigTool/pch.cpp': '767c147b79a2d6c6488f245d364e406bf927d83e92475247ce92792f71f0bb2d',
 'ConfigTool/tab_data.cpp': '5c260638480db24544ef7cac4fae6980b495a6dbef0c0cc87a7b05c81ac0972c',
 'ConfigTool/tab_data.hpp': 'c091b63a1b53534cc964798a781ecd5060adccf3c163a20310a276cf46b6814e',
 'ConfigTool/updater.cpp': 'f7ee2d0f029fba65c9eb834c811439ae49d8292580519c09d6da7b756b6b9cb6',
 'ConfigTool/updater.hpp': '234751080b7d5d39da3f239a532e5c72e12204f27c725c9de58930d9310bf0a1',
 'ConfigTool/windows_fullscreen_optimization.cpp': 'cf4ea7258d85abd9d5a7e3698bf9ab5248fb848bc98250710219ae1effc3e29e',
 'ConfigTool/windows_fullscreen_optimization.hpp': '3ba2b6564f69a89169704ba0f1ef3ca63dcb3f4d9961e6a2f33e4b9612fb27e3',
 'ConfigTool/windows_preferred_gpu.cpp': 'db02d074c2337fe40e6a9bd648555c763799566ce455c984c5d9f6858bffce74',
 'ConfigTool/windows_preferred_gpu.hpp': 'd46b6680fa24e61d84b2ea41b768ee150fbc82ef53396436d14aea4c79e98040',
 'src/dllmain.cpp': 'af0dd5d93b54358645c55da2b4bc2193461bd3dfded99e9df9d23d3c4d218d72',
 'src/features/launcher_skips_and_starts.cpp': '4800ba4eaf30ecdf0056b5fe54e30aecd0c3c59e8fd43d1b7e015154df23d207',
 'src/features/launcher_skips_and_starts.hpp': '07f6ffe24133fb1c104fb329bafcc2c0b8f7ed90eb56b06fd3d96c3f1758ce00',
 'src/features/skip_splashscreens.cpp': 'b2aeb8d3fece096bf46dc1a3f28d0261ff3a328d32bcb0f70e0eeb83537db960',
 'src/features/skip_splashscreens.hpp': 'e61a7bcf48420fa38ab8e76173f022596abfdb326df81f43704174578b9f4dc8',
 'src/fixes/ds3_rumble.cpp': '95db8146faf3c0d100d305d6678f7afd428a43e8f7ff35b47a12cfc9dc7a4e0e',
 'src/fixes/ds3_rumble.hpp': '35232a43989616d64ea47f8225ed54341db11576c261ee7a344a90de7f1aa985',
 'src/fixes/graphics_tuning.cpp': '12d028419be90bfbf717d05cee8e821aac437bb240113de6585a1e9ca3e16762',
 'src/fixes/graphics_tuning.hpp': 'ce57138a5fe65e40b3ee1ed9ca472e50d62dafa84d56a481648ba1184169db3a',
 'src/fixes/mgs4_mouse.cpp': 'b2bff6c9e22a6314426828e2d4439a91cf22e440da5d079819cd610d80d74cb6',
 'src/fixes/mgs4_mouse.hpp': 'fc18aebca94b6f5882698354509201eda0ae1744cf4b8ec13ecda576d9ae69c5',
 'src/fixes/pad_motion.cpp': '90211271c5cc1a06e87812ddc7107a34084871ceaa6d8734dbfe98472436ea48',
 'src/fixes/pad_motion.hpp': 'bf12727721726f58544a9263d667133d083b2f076f16aa6d56fc2f52ced623d0',
 'src/fixes/pressure_inputs.cpp': 'c5f9d98762ce3b09cda95c2bbc38cd440ca745d2fb1ad2e7988c2dfafd19ff79',
 'src/fixes/pressure_inputs.hpp': '25ed854cefce73648ec379802b6c6357c71438eb4812051f9ec92cbc67baeca0',
 'src/fixes/resolution_scaling_fixes.cpp': 'e6312212ef095c00e4825c74dd83446165914c85ee9f76e7881162fd2de6b92c',
 'src/fixes/resolution_scaling_fixes.hpp': 'ad6955e708fab02d6ee2aae420cd08d483e4d6625893e4bb4725c5166c39471a',
 'src/fixes/swap_menu_buttons.cpp': 'baf7c3784a3b7f3cf5be5f22a8187134ceef1f9ff29c755fef03c5d202e11036',
 'src/fixes/swap_menu_buttons.hpp': 'e54c249eddf99650d6d77c2dd2e611bea5f2efb0a4c70c88dc1a84e01b849cfc',
 'src/fixes/various_tweaks.cpp': '9a25143cf04b722b25ef6dfc06cbb95a07231447da615bf1cc06322cd9dc4987',
 'src/fixes/various_tweaks.hpp': '5f70adeb8087e0d64bb561c60e3afbd7295f248269aa4aa1d44639a89c00616c',
 'src/resources/RegStateHelpers.hpp': '718cbbd0eeff76949b91c2e2ea4fafc46bc6d28b170cb9e6f76972ea03dad405',
 'src/resources/common.hpp': '3aac103eaf5deab1cf6db8a7421dedf84cdac0ff6c4d629bf7f3bb2dbf6ec186',
 'src/resources/config.cpp': '4d2a32c4161e5802c7887c9a7557c4f42957c8b01286ca87d36609885f2be8b1',
 'src/resources/config.hpp': '469e7a729bd6c66a6692f26c0873344a23c2e20b3bd8077fa062a1da999303fb',
 'src/resources/config_keys.hpp': 'aded2e07ae05610140db3f0c26f02c0c635c176addb8947a79582f03c4bb0277',
 'src/resources/game_defines.hpp': 'b2183aacb22c4725db20129157fad7d466b652e0135a2b49da520b927bb5210d',
 'src/resources/game_stages.hpp': '586e5c870c28a3b845a00f9d4b1fd693f5adb7de46b9dcd6ba7336127268268d',
 'src/resources/gamevars.cpp': '8c2801a5e258d9c6529ec6b495e4343386cd97c88a18cf2a6c32804b7db2a122',
 'src/resources/gamevars.hpp': '0141248fb5deb056774c59394b5810c91e50e17ce242367155332af7c69100aa',
 'src/resources/gpu_check.cpp': 'e7471ea3f754bed6c306955174e6a380f25fcb527d3a5cc287640a7183f6652b',
 'src/resources/gpu_check.hpp': '9197fb0516c7befe28d891f1bee56cb74299d6dff258b0d605b6cbab9c32f19a',
 'src/resources/helper.cpp': '07d504f58806aa82cf1135be4a89ecbe28a6ec0261ce1bd003adf38b0c62df46',
 'src/resources/helper.hpp': '3c2d86cce6eb175f4ced3c756af2cc533914801ec191cfe5cda9926e60c79c13',
 'src/resources/logging.cpp': '9dbd680b57fb8c88dce37a89c874dedaa44b9921601dcec9b9747cdcc3cdd339',
 'src/resources/logging.hpp': 'ea61e3ef689ec08cc5e8468e1ea0596d07d53b785a598b73797a2d621c81c2bf',
 'src/resources/mgs4_linkvarbuf.hpp': 'c99474f329221148952bd3be3a8e5da192f2899e865050def08b1e06f9f533c7',
 'src/resources/mgspw_linkvarbuf.hpp': '119ea5c94b904e57fc4420e13de0f29db4ef639859434e2c0c8e4c38b6a7603b',
 'src/resources/stdafx.cpp': 'c2f8cfd8ea9f8110e9710a0f045c0670d202190cb1078cc3ced08d7309187bd9',
 'src/resources/submodule_initiailization.hpp': '4f434cc0897ef7b582f5aa02c47383c31d27f8f9a87719773536d2760f3cc78a',
 'src/resources/unit_tests.cpp': '04db3abec346eaebf519d8105b1d0a95de9a97ea64f3fe5f1089068ca5578ce9',
 'src/resources/unit_tests.hpp': '645242745a7035111e3749436176b84fd494b86dde13cc671cca250ad740afc5',
 'src/resources/version_checking.cpp': 'ee10225b45b332d39ff71ba14341276589eea446a53e6e7e86cc998b17e18961',
 'src/resources/version_checking.hpp': '664bd6709690d4d45724e833ee8014c50a5e435b350c612f0652b38b41e60cec',
 'src/warnings/asi_loader_checks.cpp': 'e54dc9b433b3f6dc5d5c23713e04b368425a79463db6f6134b396f77927ab1bd',
 'src/warnings/asi_loader_checks.hpp': 'b47d93b3b60ccc7930824f9818890e41652f7d164a5f621ce1c3ebd8ce1a6fe2'}


def capture(root):
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if head != TREE:
        raise ValueError("Unreviewed PatriotFix tree; source-format review required")
    actual = {str(p.relative_to(root)) for base in ("src", "ConfigTool")
              for p in (root / base).rglob("*") if p.suffix in (".cpp", ".hpp")}
    if actual != set(REVIEWED):
        raise ValueError("Source inventory changed; source-format review required")
    raw = {n: (root / n).read_bytes() for n in REVIEWED}
    for name, digest in REVIEWED.items():
        if hashlib.sha256(raw[name]).hexdigest() != digest:
            raise ValueError("Unreviewed source bytes: " + name + "; source-format review required")
    keys = without_comments(raw["src/resources/config_keys.hpp"].decode("utf-8-sig"))
    constants = dict(re.findall(r'constexpr const char\* (\w+) = (.*?);', keys, re.S))

    def value(expr):
        expr = expr.strip().replace("ConfigKeys::", "", 1)
        if expr in constants:
            return value(constants[expr])
        if expr.startswith('"'):
            return ''.join(json.loads(s) for s in re.findall(r'"(?:\\.|[^"\\])*"', expr))
        raise ValueError("Unreviewed value " + expr)

    lists = {}
    for name, body in re.findall(r'inline const std::initializer_list<std::string> (\w+) = (\{.*?\});', keys, re.S):
        lists[name] = [value(v) for v in braced(body)]
    tabs = without_comments(raw["ConfigTool/tab_data.cpp"].decode("utf-8-sig"))
    initializer = tabs.split("kTabs =", 1)[1].strip().rstrip(';').strip()
    fields = {}
    for tab in braced(initializer):
        for field in braced(braced(tab)[1]):
            parts = braced(field)
            kind = parts[7].split('::')[1]
            if kind == "Spacer":
                continue
            section, key = value(parts[1]), value(parts[2])
            entry = {"type": kind, "flags": parts[0]}
            if kind == "Bool":
                entry["default"] = int(parts[8] == "true")
            elif kind == "Int":
                entry.update(default=int(parts[8]), range=[int(v) for v in parts[9:11]])
            elif kind == "Float":
                entry.update(default=float(parts[13]), range=[float(v) for v in parts[14:16]])
            elif kind == "Choice":
                if "std::begin" in parts[12]:
                    name = re.search(r'std::begin\((\w+)\)', parts[12])[1]
                    entry["choices"] = lists[name]
                else:
                    entry["choices"] = [value(v) for v in braced(parts[12])] if parts[12] != '{}' else []
                if parts[11].startswith('*'):
                    entry["default"] = entry["choices"][0]
                else:
                    entry["default"] = value(parts[11])
            else:
                raise ValueError("Unreviewed kind " + kind)
            if key in fields.setdefault(section, {}):
                raise ValueError("Duplicate field")
            fields[section][key] = entry
    # Dynamic language choices serialize codes, from GetActiveLanguagePairs/OnSave.
    pairs = keys.split('MGS4_LanguagePairs =', 1)[1].split('} };', 1)[0]
    language_pairs = [list(map(json.loads, row)) for row in re.findall(r'\{\s*("[^"]+"),\s*("[^"]+"),\s*("[^"]+"),\s*("[^"]+")\s*\}', pairs)]
    language_pairs = [p[2:] for p in language_pairs]
    for key, idx in [("Game Region", 0), ("Game Language", 1)]:
        fields["Language Settings"][key].update(default=language_pairs[0][idx], choices=sorted({p[idx] for p in language_pairs}))
    runtime = without_comments(raw["src/resources/config.cpp"].decode("utf-8-sig"))
    reads = []
    for args in re.findall(r'ConfigHelper::getValue\((.*?)\);', runtime, re.S):
        args = split_items(args)
        section = value(args[1])
        if args[2] == "launcherSkipSetting":
            names = ["LauncherSkip_Setting", "LauncherSkip_Setting_PW"]
        elif args[2] == "ctrlTypeSetting":
            names = ["CtrlType_Setting", "CtrlType_Setting_PW"]
        else:
            names = [args[2]]
        for name in names:
            key = value(name)
            if key not in fields.get(section, {}):
                raise ValueError("Runtime key omitted: " + section + '/' + key)
            reads.append([section, key])
    return {"tag": "0.2.2", "tree": TREE, "source_sha256": REVIEWED,
            "fields": fields, "language_pairs": language_pairs,
            "runtime_reads": sorted(reads)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(capture(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
