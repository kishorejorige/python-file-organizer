#!/usr/bin/env bash
set -euo pipefail

# release.sh - create a GitHub release using the gh CLI
# Usage: ./release.sh [TAG]

TAG=${1:-}
if [ -z "$TAG" ]; then
  TAG=$(git describe --tags --abbrev=0)
fi

NOTES_FILE="/tmp/release_notes_${TAG}.md"

PREV_TAG=$(git for-each-ref --sort=-taggerdate --format '%(refname:short)' refs/tags | sed -n '2p' || true)
if [ -z "$PREV_TAG" ]; then
  git log --pretty=format:'- %s (%h)' "$TAG" > "$NOTES_FILE"
else
  git log ${PREV_TAG}..${TAG} --pretty=format:'- %s (%h)' > "$NOTES_FILE"
fi

echo "Using tag: $TAG"
echo "Release notes: $NOTES_FILE"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install it: https://github.com/cli/cli" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh is not authenticated. Run 'gh auth login' to authenticate." >&2
  exit 1
fi

echo "Creating release $TAG..."
gh release create "$TAG" --notes-file "$NOTES_FILE"
echo "Release $TAG created."
#!/usr/bin/env bash
set -euo pipefail
: "${GH_TOKEN:?Set GH_TOKEN env var with repo scope (export GH_TOKEN=...)}"
REPO="jorige3/python-file-organizer"
TAG="v1.4.0"
TITLE="v1.4.0"
NOTES_FILE="/tmp/release_notes_v1.4.0.md"

if [ ! -f "$NOTES_FILE" ]; then
  echo "Release notes not found: $NOTES_FILE" >&2
  exit 1
fi

DATA=$(jq -n --arg tag "$TAG" --arg name "$TITLE" --rawfile body "$NOTES_FILE" \
  '{tag_name:$tag, name:$name, body:$body, draft:false, prerelease:false}')

curl -sS -X POST \
  -H "Authorization: token $GH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$DATA" \
  "https://api.github.com/repos/$REPO/releases"