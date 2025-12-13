# Security Policy

## Supported Versions

We provide security updates for the following:

- **main**: Supported (actively developed)
- **latest release**: Supported (most recent tagged release)
- **older releases**: Best-effort only (may be asked to upgrade)

If you are unsure whether a version is supported, please report anyway.

## Reporting a Vulnerability

Please **do not** open public GitHub issues or pull requests for security reports.

### Preferred: Private report via GitHub Security Advisories
Use **Report a vulnerability** in the repository’s **Security** tab.

Include:
- A clear description of the issue and impact
- Steps to reproduce (proof-of-concept if available)
- Affected versions / commit hashes
- Any relevant logs, screenshots, or stack traces
- Whether the bug is exploitable remotely and any prerequisites

If the vulnerability involves data exposure, please avoid sending sensitive customer data. Redact where possible.

## What to Expect

We aim to follow coordinated vulnerability disclosure.

Typical timeline goals (may vary by severity/complexity):
- **Acknowledgement:** within **2 business days**
- **Triage / severity assessment:** within **5 business days**
- **Fix / mitigation plan:** within **10 business days**
- **Release & advisory:** as soon as practical after validation

For critical issues with active exploitation risk, we may ship mitigations sooner (e.g., configuration changes, temporary blocks) before a full patch.

## Safe Harbor

If you:
- Make a good-faith effort to follow this policy
- Avoid privacy violations, service disruption, and destructive testing
- Do not access or modify data that is not your own

…we will not pursue legal action related to your security research.

## Scope

In scope:
- The **Model Guardian** codebase (middleware, adapters, policies, API surface)
- Default configurations and examples that ship with the repo
- Dependency and supply-chain vulnerabilities that materially affect the project

Out of scope (unless clearly tied to a vulnerability in this repo):
- Issues requiring physical access
- Social engineering
- Denial-of-service tests that degrade availability
- Vulnerabilities in third-party services not controlled by this project

## Handling Sensitive Findings

If you discover a vulnerability that could affect safety-critical behavior (e.g., bypassing abstention, spoofing signals, poisoning drift baselines), please highlight:
- Whether the attack is silent (no obvious logs)
- Whether it can cause unsafe outputs or suppress refusals
- Any recommended immediate mitigations

## Security Updates

When we fix a vulnerability, we may:
- Patch the code and tag a release
- Publish a GitHub Security Advisory (recommended)
- Document mitigations/workarounds in release notes

## Third-Party Dependencies

We use third-party libraries (e.g., MAPIE, Alibi-Detect, FastAPI, scikit-learn).
If a security issue originates in a dependency, we will:
- Track upstream advisories
- Pin/upgrade versions as needed
- Publish mitigation guidance when appropriate
