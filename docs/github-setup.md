# GitHub setup

Create `secure-mcp-enterprise-toolkit` as a public repository. Upload the contents of the
extracted project folder, not a nested folder containing the whole project. Include the
.github directory. Some graphical file upload methods omit dotfiles; verify that
`.github/workflows/ci.yml` and `.github/workflows/release.yml` appear on GitHub.

CI runs on push and pull requests and can be started manually. Wait for tests and container
checks to pass. Fix an actual failing step before publishing. Workflow definitions alone
are not evidence that GitHub has run them.

## Release and package

Open Actions → Release and package → Run workflow on main. The workflow derives v0.1.0
from pyproject.toml, runs tests, builds a wheel and source ZIP, builds/smoke-tests Docker,
pushes `ghcr.io/OWNER/secure-mcp-enterprise-toolkit:v0.1.0`, then publishes a GitHub release.
It needs contents:write and packages:write; organization policy can restrict these grants.
No personal access token is required for this workflow's GITHUB_TOKEN.

A new package may be private initially. In its settings, choose public visibility if you
intend anonymous downloads. Inspect the built package/version rather than assuming a
successful file upload has published a package. Set repository About to show Releases and
Packages. GitHub source label links the image to the source repository.

If the release already exists, increase the project version and update RELEASE_NOTES.md
before a new release. Do not delete an existing version merely to rerun the workflow.
README-only changes do not require another package release.

## About and discovery

Use the description and topics in README.md. Add a public demo/video URL only if one exists;
localhost is not a public deployment. Pin the repository on your profile and share actual
screenshots or a recording. Stars should come from real users who find the project useful.
