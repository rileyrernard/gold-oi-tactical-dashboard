"""Copy the complete public skill to one agent scope without overwriting files."""
import argparse
import hashlib
import shutil
from pathlib import Path

NAME = 'gold-oi-tactical-dashboard'

def manifest(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}

def install(agent, project=None, user=False, user_home=None):
    source = Path(__file__).resolve().parents[1] / 'skills' / NAME
    home = Path(user_home) if user_home else Path.home()
    if user:
        base = {'codex': home/'.agents/skills', 'claude': home/'.claude/skills',
                'antigravity': home/'.gemini/config/skills'}[agent]
    else:
        if not project or not Path(project).is_dir():
            raise ValueError('--project must name an existing project directory')
        base = Path(project).resolve() / ('.claude/skills' if agent == 'claude' else '.agents/skills')
    target = base/NAME
    expected = manifest(source)
    if target.exists():
        if not target.is_dir() or manifest(target) != expected:
            raise ValueError(f'Existing target differs; back it up and resolve manually: {target}')
        print(f'Already installed (hash verified): {target}')
        return target
    base.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    if manifest(target) != expected:
        raise RuntimeError(f'Copied skill verification failed: {target}')
    print(f'Installed {len(expected)} files (SHA-256 verified): {target}')
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', required=True, choices=['codex','claude','antigravity'])
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument('--project', type=Path)
    scope.add_argument('--user', action='store_true', help='Antigravity App/IDE global scope; use project scope for CLI')
    args = parser.parse_args()
    try:
        install(args.agent, args.project, args.user)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'INSTALL_ERROR: {exc}\n')
