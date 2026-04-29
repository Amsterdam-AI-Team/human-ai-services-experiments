#!/usr/bin/env bash
# Build the SvelteKit app and bundle a deploy.zip suitable for
# `az webapp deploy --type zip` to an Azure App Service (Linux, Node 20).
#
# What ends up in the zip:
#   - build/             (adapter-node output incl. static assets)
#   - package.json       (with "start": "node build")
#   - package-lock.json  (so Azure's Oryx runs `npm ci` deterministically)
#
# Excluded on purpose: node_modules, .git, .env, .svelte-kit, source files.
# Azure unpacks the zip and (with SCM_DO_BUILD_DURING_DEPLOYMENT=true)
# runs `npm install` to materialise runtime dependencies.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/frontend"
ZIP_PATH="$SCRIPT_DIR/deploy.zip"

cd "$APP_DIR"

if [ ! -f .env ]; then
	echo "ERROR: frontend/.env not found." >&2
	echo "       cp .env.example .env  and fill in values from your Azure resource." >&2
	echo "       See DEPLOY_ENV_VARS.md for what each key does." >&2
	exit 1
fi

echo "==> npm ci"
npm ci

echo "==> npm run build"
npm run build

if [ ! -d build ] || [ ! -f build/index.js ]; then
	echo "ERROR: build/index.js missing — vite build did not produce the expected" >&2
	echo "       adapter-node output. Check svelte.config.js." >&2
	exit 1
fi

echo "==> packaging $ZIP_PATH"
rm -f "$ZIP_PATH"
zip -rq "$ZIP_PATH" \
	build \
	package.json \
	package-lock.json \
	-x "*.DS_Store"

SIZE=$(du -h "$ZIP_PATH" | cut -f1)
echo "==> $ZIP_PATH ready ($SIZE)"

cat <<EOF

Before deploying, in Azure Portal → App Service → Settings → Environment
variables, set at minimum:

  SCM_DO_BUILD_DURING_DEPLOYMENT=true     (so Oryx runs \`npm install\` post-unzip)
  WEBSITE_NODE_DEFAULT_VERSION=~20         (or pin via App Service stack settings)

Plus every variable listed in DEPLOY_ENV_VARS.md.

Then deploy:

  az webapp deploy \\
    --resource-group <RESOURCE_GROUP> \\
    --name <APP_NAME> \\
    --src-path "$ZIP_PATH" \\
    --type zip

EOF
