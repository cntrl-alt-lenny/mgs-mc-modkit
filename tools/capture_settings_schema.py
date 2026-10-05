#!/usr/bin/env python3
"""Capture a bounded static MGS2/MGS3 Config Tool schema, not a binary export.

Supports the reviewed 4.1.0/4.1.1/4.1.2 kTabs initializer layout. Game flags
are MG/MGS2/MGS3, OR expressions, and constexpr int aliases (including the
union of both branches of #if defined(NAME)/#else). No preprocessor evaluation
or claim of release-build MGS3 FPS applicability is made. Unreviewed field or
flag syntax requires source-format review. Dynamic choices, float bounds and
defaults are not captured; actual per-game Config Tool exports remain required.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


class CaptureError(RuntimeError):
    """Input is outside the reviewed static declaration format."""


def fail(construct):
    raise CaptureError(f"Unsupported source construct: {construct[:180]}; review the upstream source format")


STRING = r'"(?:\\.|[^"\\])*"'


def without_comments(text):
    # Preserve strings (including comment markers) while removing comments.
    return re.sub(STRING + r'|//[^\n]*|/\*.*?\*/',
                  lambda m: m.group() if m.group().startswith('"') else ' ', text, flags=re.S)


def split_items(text, separator=','):
    """Split only at top level, checking all brackets and quoted strings."""
    result, stack, start = [], [], 0
    tokens = re.finditer(STRING + r'|["(){}\[\]]|' + re.escape(separator), text)
    for token in tokens:
        value = token.group()
        if value.startswith('"'):
            if value == '"':
                fail('unterminated string: ' + text)
            continue
        if value in '({[':
            stack.append(value)
        elif value in ')}]':
            if not stack or stack.pop() != {')': '(', '}': '{', ']': '['}[value]:
                fail('unbalanced initializer: ' + text)
        elif not stack:
            result.append(text[start:token.start()].strip())
            start = token.end()
    if stack:
        fail('unclosed initializer: ' + text)
    result.append(text[start:].strip())
    if result[-1] == '' and separator == ',':
        result.pop()  # reviewed trailing comma
    if any(not item for item in result):
        fail('empty initializer item: ' + text)
    return result


def braced(text):
    if not text.startswith('{') or not text.endswith('}'):
        fail('expected braced initializer: ' + text)
    return split_items(text[1:-1])


def flag_names(expression, definitions, visiting=()):
    expression = expression.strip()
    if expression.startswith('(') and expression.endswith(')'):
        # Only strip an enclosing pair, not (MGS2)|(MGS3).
        parts = split_items(expression, '|')
        if len(parts) == 1:
            return flag_names(expression[1:-1], definitions, visiting)
    parts = split_items(expression, '|')
    if len(parts) > 1:
        return set().union(*(flag_names(p, definitions, visiting) for p in parts))
    if expression in {'MG', 'MGS2', 'MGS3'}:
        return {expression}
    if not re.fullmatch(r'\w+', expression) or expression not in definitions:
        fail('game flags ' + expression)
    if expression in visiting:
        fail('cyclic game flag alias ' + expression)
    return set().union(*(flag_names(p, definitions, visiting + (expression,))
                         for p in definitions[expression]))


def flag_definitions(prefix):
    prefix = re.sub(r'^\s*#include[^\n]*', '', prefix, flags=re.M).strip()
    definitions = {}
    declaration = r'constexpr\s+int\s+(\w+)\s*=\s*([^;]+);'
    conditional = (r'#if\s+defined\(\w+\)\s*(' + declaration + r')\s*'
                   r'#else\s*(' + declaration + r')\s*#endif')
    while prefix:
        match = re.match(conditional, prefix)
        if match:
            _, name, first, _, other_name, second = match.groups()
            if name != other_name:
                fail('conditional aliases must name the same flag: ' + match.group())
            expressions = [first, second]
        else:
            match = re.match(declaration, prefix)
            if not match:
                fail('flag declarations/preprocessor ' + prefix)
            name, expression = match.groups()
            expressions = [expression]
        if name in definitions or name in {'MG', 'MGS2', 'MGS3'}:
            fail('duplicate/reserved flag alias ' + name)
        definitions[name] = expressions
        prefix = prefix[match.end():].strip()
    # Review unused aliases too: unknown syntax must not hide in an excluded field.
    for name in definitions:
        flag_names(name, definitions)
    return definitions


def constant_values(text):
    """Read only the complete, unconditional, reviewed ConfigKeys namespace."""
    namespace = re.compile(STRING + r'|\bnamespace\s+ConfigKeys\s*\{')
    matches = [m for m in namespace.finditer(text) if not m.group().startswith('"')]
    if len(matches) != 1:
        fail('ConfigKeys namespace declaration')
    opening = matches[0]

    # Anchor the namespace at global scope. Only the reviewed preamble is
    # allowed: arbitrary includes/macros/declarations could redirect references.
    preamble = text[:opening.start()].strip()
    guard = r'#if !defined\(_CRT_SECURE_NO_WARNINGS\)\s*#define _CRT_SECURE_NO_WARNINGS\s*#endif'
    wrapper = (r'(?:#pragma once\s*)?'
               r'(?:' + guard + r'\s*)?'
               r'(?:#include <string>\s*#include <initializer_list>\s*)?')
    if not re.fullmatch(wrapper, preamble):
        if re.search(r'^\s*#\s*(?:if|ifdef|ifndef)\b', preamble, re.M):
            fail('conditional context around ConfigKeys namespace: ' + preamble)
        fail('header context before ConfigKeys namespace: ' + preamble)

    depth, closing = 1, None
    for token in re.finditer(STRING + r'|[{}]', text[opening.end():]):
        value = token.group()
        if value.startswith('"'):
            continue
        if value == '{':
            depth += 1
            if depth > 1:
                fail('nested ConfigKeys namespace')
        else:
            depth -= 1
            if depth == 0:
                closing = opening.end() + token.start()
                break
    if closing is None:
        fail('unclosed ConfigKeys namespace')
    # The reviewed releases share an identical noncanonical tail (controller
    # lists, language helpers and camera bounds). Accept its exact lexical token
    # sequence, or an empty tail for minimal headers; never skip other code.
    # Fingerprint is independently reproduced from all three immutable sources.
    tail = text[closing + 1:]
    tokens = re.findall(STRING + r'|[A-Za-z_][A-Za-z_0-9]*|[0-9]+|\S', tail)
    reviewed_tail = '8ade693eb22bd65377db0fed88492cb132ce0213af49d05d3b49fc00546e39fd'
    if tokens and hashlib.sha256('\0'.join(tokens).encode()).hexdigest() != reviewed_tail:
        fail('header context after ConfigKeys namespace: ' + tail.strip())

    body = text[opening.end():closing]
    if re.search(r'^\s*#', body, re.M):
        fail('preprocessor directive in ConfigKeys namespace')

    declarations = {}
    pattern = re.compile(
        r'constexpr\s+const\s+char\*\s+(\w+)\s*=\s*'
        r'((?:' + STRING + r'\s*)+|\w+)\s*;')
    cursor = 0
    for match in pattern.finditer(body):
        if body[cursor:match.start()].strip():
            fail('unsupported ConfigKeys declaration ' + body[cursor:match.start()].strip())
        name, expression = match.groups()
        if name in declarations:
            fail('duplicate string constant ' + name)
        declarations[name] = expression.strip()
        cursor = match.end()
    if body[cursor:].strip():
        fail('unsupported ConfigKeys declaration ' + body[cursor:].strip())
    if not declarations:
        fail('empty ConfigKeys namespace')

    def resolve(name, visiting=()):
        if name not in declarations or name in visiting:
            fail('missing/cyclic string constant ' + name)
        expression = declarations[name]
        if expression.startswith('"'):
            try:
                return ''.join(json.loads(s) for s in re.findall(STRING, expression))
            except ValueError:
                fail('unsupported string escape in ' + name)
        return resolve(expression, visiting + (name,))

    return resolve


def capture(root, tag, tree):
    sources = ['ConfigTool/tab_data.cpp', 'src/resources/config_keys.hpp']
    original = {name: (root / name).read_bytes() for name in sources}
    tabs, keys = [without_comments(original[name].decode('utf-8-sig')) for name in sources]
    constant = constant_values(keys)
    header = re.search(r'const\s+std::vector<std::pair<wxString,\s*std::vector<Field>>>\s+kTabs\s*=\s*', tabs)
    if not header or tabs.count('kTabs') != 1:
        fail('expected one reviewed kTabs declaration')
    definitions = flag_definitions(tabs[:header.start()])
    initializer = tabs[header.end():].strip()
    if not initializer.endswith(';'):
        fail('kTabs must end with a semicolon')
    fields, constraints = {}, {}
    for tab in braced(initializer[:-1].strip()):
        pair = braced(tab)
        if len(pair) != 2 or not re.fullmatch(r'wxString\(' + STRING + r'\)', pair[0]):
            fail('tab wrapper ' + tab)
        for declaration in braced(pair[1]):
            parts = braced(declaration)
            if len(parts) < 8 or len(parts) > 17:
                fail('field initializer ' + declaration)
            flags = flag_names(parts[0], definitions)
            kind_match = re.fullmatch(r'Field::(Bool|Int|Float|Str|Choice|Hotkey|Spacer)', parts[7])
            if not kind_match:
                fail('field type ' + declaration)
            kind = kind_match.group(1)
            lengths = {'Bool': {9}, 'Int': {11, 17}, 'Float': {15, 16},
                       'Str': {12}, 'Choice': {13}, 'Hotkey': {12}, 'Spacer': {8}}
            if len(parts) not in lengths[kind]:
                fail('field argument layout ' + declaration)
            section_match = re.fullmatch(r'ConfigKeys::(\w+)_Section', parts[1])
            key_match = re.fullmatch(r'ConfigKeys::(\w+)_Setting', parts[2])
            # Only these reviewed non-canonical UI rows are excluded. Other literal
            # or computed keys stop capture rather than disappearing silently.
            if kind == 'Spacer':
                if parts[2] != '""':
                    fail('spacer key ' + declaration)
                continue
            if (parts[1:3] == ['ConfigKeys::ResetAllAchievements_Section', '"Safety Switch"']
                    and kind == 'Bool'):
                continue
            if not section_match or not key_match:
                fail('canonical section/key ' + declaration)
            section = constant(section_match.group(1) + '_Section')
            key = constant(key_match.group(1) + '_Setting')
            if not {'MGS2', 'MGS3'} & flags:
                continue
            if not section or not key or key in fields.get(section, {}):
                fail('empty/duplicate canonical field ' + declaration)
            fields.setdefault(section, {})[key] = kind
            constraint = {}
            if kind == 'Choice':
                if len(parts) < 13:
                    fail('choice initializer ' + declaration)
                options = braced(parts[12])
                if options == ['std::begin(kLauncherConfigCtrlTypes)', 'std::end(kLauncherConfigCtrlTypes)']:
                    pass  # reviewed dynamic list, intentionally not captured
                elif options:
                    values = []
                    for option in options:
                        match = re.fullmatch(r'ConfigKeys::(\w+)', option)
                        if match:
                            values.append(constant(match.group(1)))
                        elif re.fullmatch(STRING, option):
                            try:
                                values.append(json.loads(option))
                            except ValueError:
                                fail('unsupported choice string escape ' + option)
                        else:
                            fail('choice value ' + option)
                    constraint['choices'] = values
            elif kind == 'Int' and len(parts) >= 11:
                known = {'D3D11_REQ_TEXTURE2D_U_OR_V_DIMENSION': 16384,
                         'D3D11_DEFAULT_MAX_ANISOTROPY': 16}
                values = []
                for bound in parts[9:11]:
                    if re.fullmatch(r'-?\d+', bound):
                        values.append(int(bound))
                    elif bound in known:
                        values.append(known[bound])
                    elif bound in {'k3rdPersonMinCameraDistance', 'k3rdPersonMaxCameraDistance'}:
                        values.append(None)  # reviewed opaque bound, unchanged limit
                    else:
                        fail('integer bound ' + bound)
                if None not in values:
                    constraint['range'] = values
            if constraint:
                constraints.setdefault(section, {})[key] = constraint
    if not fields:
        fail('no canonical MGS2/MGS3 fields recognized')
    result = {'upstream': 'ShizCalev/MGSHDFix', 'tag': tag, 'tree': tree,
              'sources': sources,
              'fields': {s: dict(sorted(fields[s].items())) for s in sorted(fields)},
              'constraints': constraints,
              'source_sha256': {name: hashlib.sha256(data).hexdigest() for name, data in original.items()}}
    if definitions:
        result['flag_unions'] = {name: sorted(flag_names(name, definitions)) for name in definitions}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('upstream_checkout', type=Path)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--tree', required=True)
    args = parser.parse_args()
    try:
        data = capture(args.upstream_checkout, args.tag, args.tree)
    except CaptureError as error:
        parser.exit(1, f'capture failed: {error}\n')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
