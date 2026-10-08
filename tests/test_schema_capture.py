"""Fail-closed static capture, independent of network and installer behavior."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools import capture_settings_schema as capture


CONSTANTS = '''
namespace ConfigKeys {
constexpr const char* Demo_Section = "First Person Shooter Mode";
constexpr const char* Demo_Setting = "Enable First Person Shooter Mode";
constexpr const char* Move_Section = Demo_Section;
constexpr const char* Move_Setting = "First Person Shooter - Movement Enabled By Default";
constexpr const char* Toggle_Section = Demo_Section;
constexpr const char* Toggle_Setting = "Toggle First Person Shooter Movement";
constexpr const char* Sound_Section = "System Specific Fixes";
constexpr const char* Sound_Setting = "Audio Output Mode";
constexpr const char* Stereo = "Stereo (2.0)";
constexpr const char* Surround = "Surround Sound (5.1)";
constexpr const char* Width_Section = "Window Settings";
constexpr const char* Width_Setting = "Window Width";
}
'''
ROWS = '''
{ (FLAGS), ConfigKeys::Demo_Section, ConfigKeys::Demo_Setting,
  "// literal, not a comment", "", std::nullopt, false, Field::Bool, false },
{ (FLAGS), ConfigKeys::Move_Section, ConfigKeys::Move_Setting,
  "", "", std::nullopt, false, Field::Bool, true },
{ (FLAGS), ConfigKeys::Toggle_Section, ConfigKeys::Toggle_Setting,
  "", "", std::nullopt, false, Field::Hotkey, 0, 0, 0, "Down" },
{ (MGS2|MGS3), ConfigKeys::Sound_Section, ConfigKeys::Sound_Setting,
  "", "", std::nullopt, false, Field::Choice, 0, 0, 0, "",
  {ConfigKeys::Stereo, ConfigKeys::Surround} },
{ (MGS3), ConfigKeys::Width_Section, ConfigKeys::Width_Setting,
  "", "", std::make_pair(ConfigKeys::Sound_Section, ConfigKeys::Sound_Setting),
  false, Field::Int, 0, 0, D3D11_REQ_TEXTURE2D_U_OR_V_DIMENSION },
{ (MG), "About", "", "", "", std::nullopt, false, Field::Spacer },
'''
ALIAS = '''
#if defined(MGS3_FPS_DEV)
constexpr int kFirstPersonViewGameFlags = MGS2 | MGS3;
#else
constexpr int kFirstPersonViewGameFlags = MGS2;
#endif
'''
FPS = {
    'Enable First Person Shooter Mode': 'Bool',
    'First Person Shooter - Movement Enabled By Default': 'Bool',
    'Toggle First Person Shooter Movement': 'Hotkey',
}


def source(tmp_path, flags='MGS2', prefix='', rows=ROWS, constants=CONSTANTS):
    tabs = (prefix + '\nconst std::vector<std::pair<wxString, std::vector<Field>>> kTabs = {\n'
            '{ wxString("Demo"), {\n' + rows.replace('FLAGS', flags) + '\n}}\n};\n')
    for name, text in [('ConfigTool/tab_data.cpp', tabs), ('src/resources/config_keys.hpp', constants)]:
        dest = tmp_path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b'\xef\xbb\xbf' + text.replace('\n', '\r\n').encode())
    return tmp_path


def test_baseline_exact_fields_and_constraints(tmp_path):
    data = capture.capture(source(tmp_path), 'test', 'immutable')
    assert data['fields'] == {
        'First Person Shooter Mode': FPS,
        'System Specific Fixes': {'Audio Output Mode': 'Choice'},
        'Window Settings': {'Window Width': 'Int'},
    }
    assert data['constraints'] == {
        'System Specific Fixes': {'Audio Output Mode': {'choices': ['Stereo (2.0)', 'Surround Sound (5.1)']}},
        'Window Settings': {'Window Width': {'range': [0, 16384]}},
    }
    assert 'flag_unions' not in data


@pytest.mark.parametrize('prefix', [ALIAS, 'constexpr int kFirstPersonViewGameFlags = (MGS2 | MGS3);'])
def test_alias_keeps_all_three_exact_fields_and_original_hashes(tmp_path, prefix):
    root = source(tmp_path, 'kFirstPersonViewGameFlags', prefix)
    original = {name: (root / name).read_bytes() for name in ['ConfigTool/tab_data.cpp', 'src/resources/config_keys.hpp']}
    data = capture.capture(root, '4.1.2', 'literal-commit')
    assert data['fields']['First Person Shooter Mode'] == FPS
    assert data['flag_unions'] == {'kFirstPersonViewGameFlags': ['MGS2', 'MGS3']}
    assert data['source_sha256'] == {name: hashlib.sha256(raw).hexdigest() for name, raw in original.items()}
    assert all((root / name).read_bytes() == raw for name, raw in original.items())


def test_alias_chain_and_parenthesized_union(tmp_path):
    prefix = 'constexpr int Base = MG;\nconstexpr int Target = Base | (MGS2 | MGS3);'
    data = capture.capture(source(tmp_path, 'Target', prefix), 'test', 'tree')
    assert data['fields']['First Person Shooter Mode'] == FPS
    assert data['flag_unions']['Target'] == ['MG', 'MGS2', 'MGS3']


def test_hidden_game_fields_are_saved_too(tmp_path):
    data = capture.capture(source(tmp_path, 'MG'), 'test', 'tree')
    assert data['fields']['First Person Shooter Mode'] == FPS
    assert len(data['fields']) == 3


@pytest.mark.parametrize('flags', ['UNKNOWN', 'MGS2_NEW', 'MGS2 & MGS3', 'MGS2 |',
                                   'MGS2 || MGS3', '0', '(MGS2', 'makeFlags(MGS2)'])
def test_unknown_or_malformed_flags_never_succeed_partially(tmp_path, flags):
    with pytest.raises(RuntimeError, match='review.*source.*format'):
        capture.capture(source(tmp_path, flags), 'test', 'tree')


@pytest.mark.parametrize('prefix', [
    '#ifdef MGS3_FPS_DEV\nconstexpr int Target = MGS2;\n#endif',
    '#if defined(TEST)\nconstexpr int Target = MGS2;\n#else\nconstexpr int Other = MGS3;\n#endif',
    '#if defined(TEST)\nconstexpr int Target = MGS2;\n#endif',
    'constexpr int Target = Unknown;',
    'constexpr int Target = Target;',
    'constexpr int Target = MGS2;\nconstexpr int Target = MGS3;',
])
def test_unsupported_aliases_fail_even_if_unused(tmp_path, prefix):
    with pytest.raises(RuntimeError, match='review.*source.*format'):
        capture.capture(source(tmp_path, prefix=prefix), 'test', 'tree')


@pytest.mark.parametrize('rows', [
    ROWS.replace('ConfigKeys::Demo_Setting', '"New literal key"', 1),
    ROWS.replace('ConfigKeys::Demo_Section', 'sectionForGame()', 1),
    ROWS.replace('Field::Bool', 'Field::NewType', 1),
    ROWS.replace('Field::Bool, false', 'false', 1),
    ROWS.replace('Field::Bool, false', 'Field::Bool', 1),
    ROWS.replace('Field::Bool, false }', 'Field::Bool, false ', 1),
    ROWS + '{ MGS2, MissingSection, MissingKey },',
    ROWS.replace('D3D11_REQ_TEXTURE2D_U_OR_V_DIMENSION', 'UNKNOWN_BOUND'),
    ROWS.replace('ConfigKeys::Surround}', 'dynamicNewChoices()}'),
    ROWS + ROWS,
])
def test_unrecognized_declarations_fail_without_partial_output(tmp_path, rows):
    with pytest.raises(RuntimeError, match='review.*source.*format'):
        capture.capture(source(tmp_path, rows=rows), 'test', 'tree')


def test_missing_canonical_constant_is_actionable(tmp_path):
    with pytest.raises(RuntimeError, match='Demo_Setting.*review.*source.*format'):
        capture.capture(source(tmp_path, constants=CONSTANTS.replace('Demo_Setting', 'Changed_Setting')), 'test', 'tree')


@pytest.mark.parametrize('declaration', [
    '#if defined(NEW_FORMAT)\n'
    'constexpr char const* Demo_Setting = "Replacement Key";\n'
    '#else\n'
    'constexpr const char* Demo_Setting = "Enable First Person Shooter Mode";\n'
    '#endif',
    '#if defined(NEW_FORMAT)\n'
    'constexpr const char* Demo_Setting = "Enable First Person Shooter Mode";\n'
    '#else\n'
    'constexpr char const* Demo_Setting = "Replacement Key";\n'
    '#endif',
    '#if defined(NEW_FORMAT)\n'
    'constexpr char const* Demo_Section = "Replacement Section";\n'
    '#else\n'
    'constexpr const char* Demo_Section = "First Person Shooter Mode";\n'
    '#endif',
    '#if defined(NEW_FORMAT)\n'
    'constexpr char const* Surround = "Replacement Choice";\n'
    '#else\n'
    'constexpr const char* Surround = "Surround Sound (5.1)";\n'
    '#endif',
])
def test_conditional_canonical_strings_fail_through_api(tmp_path, declaration):
    target = 'constexpr const char* Demo_Setting = "Enable First Person Shooter Mode";'
    if 'Demo_Section' in declaration:
        target = 'constexpr const char* Demo_Section = "First Person Shooter Mode";'
    elif 'Surround' in declaration:
        target = 'constexpr const char* Surround = "Surround Sound (5.1)";'
    constants = CONSTANTS.replace(target, declaration)
    with pytest.raises(RuntimeError, match='preprocessor directive.*review.*source.*format'):
        capture.capture(source(tmp_path, constants=constants), 'test', 'tree')


@pytest.mark.parametrize('body', [
    '#if defined(NEW_FORMAT)\nconstexpr const char* Demo_Setting = "Replacement Key";\n#endif',
    'namespace Nested { constexpr const char* Demo_Setting = "Replacement Key"; }',
    'constexpr char const* Demo_Setting = "Replacement Key";',
    'constexpr const char* Demo_Setting = "Enable First Person Shooter Mode";\n'
    'constexpr const char* Demo_Setting = "Replacement Key";',
])
def test_unreviewed_configkeys_context_or_declaration_fails(tmp_path, body):
    constants = CONSTANTS.replace(
        'constexpr const char* Demo_Setting = "Enable First Person Shooter Mode";', body)
    with pytest.raises(RuntimeError, match='review.*source.*format'):
        capture.capture(source(tmp_path, constants=constants), 'test', 'tree')


def test_conditional_namespace_wrapper_fails(tmp_path):
    constants = '#if defined(NEW_FORMAT)\n' + CONSTANTS + '#endif\n'
    with pytest.raises(RuntimeError, match='conditional context.*review.*source.*format'):
        capture.capture(source(tmp_path, constants=constants), 'test', 'tree')


def test_cli_failure_has_no_json_and_identifies_offending_flag(tmp_path):
    root = source(tmp_path, 'UNKNOWN_FLAGS')
    result = subprocess.run([sys.executable, str(Path(capture.__file__)), str(root), '--tag', 'test', '--tree', 'tree'],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert result.stdout == ''
    assert 'UNKNOWN_FLAGS' in result.stderr
    assert 'review the upstream source format' in result.stderr


def test_conditional_canonical_string_cli_failure_has_no_partial_json(tmp_path):
    constants = CONSTANTS.replace(
        'constexpr const char* Demo_Setting = "Enable First Person Shooter Mode";',
        '#if defined(NEW_FORMAT)\n'
        'constexpr char const* Demo_Setting = "Replacement Key";\n'
        '#else\n'
        'constexpr const char* Demo_Setting = "Enable First Person Shooter Mode";\n'
        '#endif')
    result = subprocess.run(
        [sys.executable, str(Path(capture.__file__)),
         str(source(tmp_path, constants=constants)), '--tag', 'test', '--tree', 'tree'],
        capture_output=True, text=True)
    assert result.returncode == 1
    assert result.stdout == ''
    assert 'preprocessor directive in ConfigKeys namespace' in result.stderr
    assert 'review the upstream source format' in result.stderr


def test_cli_success_is_json_with_identity_and_unmodified_hashes(tmp_path):
    root = source(tmp_path, 'kFirstPersonViewGameFlags', ALIAS)
    result = subprocess.run([sys.executable, str(Path(capture.__file__)), str(root), '--tag', 'test', '--tree', 'tree'],
                            capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    assert data['tag'] == 'test' and data['tree'] == 'tree'
    assert data['fields']['First Person Shooter Mode'] == FPS
    assert data['source_sha256']['ConfigTool/tab_data.cpp'] == hashlib.sha256((root / 'ConfigTool/tab_data.cpp').read_bytes()).hexdigest()


REVIEWED_TAIL = (Path(__file__).parent / 'fixtures/hdfix-reviewed-header-tail.hpp').read_text()
DECOY_ALIAS = ('namespace Decoy {\n' + CONSTANTS + '\n}\n'
               + CONSTANTS.replace('namespace ConfigKeys {', 'namespace Actual {').replace(
                   'Enable First Person Shooter Mode', 'Replacement Key')
               + '\nnamespace ConfigKeys = Actual;\n')


@pytest.mark.parametrize('constants', [
    DECOY_ALIAS,
    'namespace Decoy {\n' + CONSTANTS + '\n}',
    'namespace {\n' + CONSTANTS + '\n}',
    'inline namespace Decoy {\n' + CONSTANTS + '\n}',
    CONSTANTS.replace('namespace ConfigKeys {', 'namespace Decoy::ConfigKeys {'),
    CONSTANTS.replace('namespace ConfigKeys {', 'inline namespace ConfigKeys {'),
    CONSTANTS.replace('namespace ConfigKeys {', 'namespace ConfigKeys [[deprecated]] {'),
    'namespace ConfigKeys {}\n' + CONSTANTS,
    'namespace Actual {}\n' + CONSTANTS + 'namespace ConfigKeys = Actual;',
    CONSTANTS + 'namespace Other { constexpr int Value = 1; }',
    CONSTANTS + 'using namespace Other;',
    CONSTANTS + 'constexpr int Extra = 1;',
    CONSTANTS + '\n#define ConfigKeys Actual\n',
    '#define ConfigKeys Actual\n' + CONSTANTS,
    '#include "unreviewed.hpp"\n' + CONSTANTS,
    '#if defined(TEST)\nnamespace Other {}\n#endif\n' + CONSTANTS,
    CONSTANTS + REVIEWED_TAIL + 'namespace ConfigKeys = Actual;',
    CONSTANTS + REVIEWED_TAIL.replace('static bool', 'namespace Other {}\nstatic bool', 1),
])
def test_namespace_boundary_rejects_api_and_cli(tmp_path, constants):
    root = source(tmp_path, constants=constants)
    with pytest.raises(capture.CaptureError, match='review the upstream source format'):
        capture.capture(root, 'test', 'tree')
    result = subprocess.run(
        [sys.executable, str(Path(capture.__file__)), str(root), '--tag', 'test', '--tree', 'tree'],
        capture_output=True, text=True)
    assert result.returncode == 1
    assert result.stdout == ''
    assert 'capture failed: Unsupported source construct:' in result.stderr
    assert 'review the upstream source format' in result.stderr


@pytest.mark.parametrize('tail', ['', REVIEWED_TAIL, '\n// harmless comment\n' + REVIEWED_TAIL])
@pytest.mark.parametrize('preamble', [
    '', '#pragma once\n',
    '#pragma once\n#if !defined(_CRT_SECURE_NO_WARNINGS)\n'
    '#define _CRT_SECURE_NO_WARNINGS\n#endif\n#include <string>\n#include <initializer_list>\n',
])
def test_reviewed_header_context_preserves_literals_aliases_and_hashes(tmp_path, preamble, tail):
    constants = CONSTANTS.replace('"First Person Shooter Mode"', '"First Person " "Shooter Mode"')
    constants = constants.replace('"Stereo (2.0)"', '"Stereo (2.0)" /* namespace ConfigKeys = Decoy; */')
    constants += '// namespace Decoy { namespace ConfigKeys {} }\n'
    root = source(tmp_path, constants=preamble + constants + tail)
    expected = capture.capture(source(tmp_path / 'baseline'), 'test', 'tree')
    actual = capture.capture(root, 'test', 'tree')
    assert actual['fields'] == expected['fields']
    assert actual['constraints'] == expected['constraints']
    assert actual['source_sha256']['src/resources/config_keys.hpp'] == hashlib.sha256(
        (root / 'src/resources/config_keys.hpp').read_bytes()).hexdigest()


def test_namespace_spelling_inside_string_is_not_a_declaration(tmp_path):
    constants = CONSTANTS.replace('"Stereo (2.0)"', '"namespace ConfigKeys { // literal }"')
    data = capture.capture(source(tmp_path, constants=constants), 'test', 'tree')
    assert data['constraints']['System Specific Fixes']['Audio Output Mode']['choices'][0] == (
        'namespace ConfigKeys { // literal }')
